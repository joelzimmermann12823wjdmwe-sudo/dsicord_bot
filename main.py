from __future__ import annotations

import asyncio
import functools
import gc
import os
import sys
import threading
import traceback
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from monitoring import DiscordApiLimiter, ExecutionGate, RuntimeMonitor, log_event, start_status_server
from storage import Storage

BASE_DIR = Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"

COMMAND_CONCURRENCY_LIMIT = 8
API_CONCURRENCY_LIMIT = 2
API_MIN_INTERVAL_SECONDS = 0.35
MESSAGE_CACHE_LIMIT = 250
STORAGE_HEALTHCHECK_INTERVAL_SECONDS = 300
MEMORY_CLEANUP_INTERVAL_SECONDS = 1800
STATS_LOG_INTERVAL_SECONDS = 21600


def build_intents() -> discord.Intents:
    intents = discord.Intents.none()
    intents.guilds = True
    intents.guild_messages = True
    intents.dm_messages = True
    intents.members = True
    intents.message_content = True
    intents.voice_states = True
    intents.moderation = True
    return intents


def build_member_cache_flags() -> discord.MemberCacheFlags:
    flags = discord.MemberCacheFlags.none()
    flags.voice = True
    return flags


def default_permissions() -> dict[str, list[int]]:
    return {
        "owner": [],
        "admins": [],
        "developers": [],
        "banned_servers": [],
        "banned_users": [],
    }


def get_int_env(name: str) -> int | None:
    value = (os.getenv(name) or "").strip()
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        log_event("warning", "invalid_env_int", env=name, value=value)
        return None


def get_allowed_guild_id() -> int | None:
    return get_int_env("ALLOWED_GUILD_ID")


def get_status_port() -> int:
    raw = (os.getenv("PORT") or "8000").strip()
    try:
        return int(raw)
    except ValueError:
        log_event("warning", "invalid_port", value=raw)
        return 8000


def get_public_status_base_url() -> str:
    public_url = (
        os.getenv("STATUS_PUBLIC_BASE_URL")
        or os.getenv("PUBLIC_STATUS_BASE_URL")
        or os.getenv("RENDER_EXTERNAL_URL")
        or ""
    ).strip()
    if public_url:
        return public_url.rstrip("/")
    return f"http://127.0.0.1:{get_status_port()}"


def is_allowed_guild(guild: discord.abc.Snowflake | None) -> bool:
    allowed_guild_id = get_allowed_guild_id()
    if allowed_guild_id is None or guild is None:
        return True
    return guild.id == allowed_guild_id


def format_exception_text(error: BaseException) -> str:
    root_error = getattr(error, "original", error)
    return "".join(traceback.format_exception_only(type(root_error), root_error)).strip()[:1000]


def get_retry_after(error: discord.HTTPException, attempt: int) -> int:
    headers = getattr(error.response, "headers", {}) or {}
    retry_after = headers.get("Retry-After")
    if retry_after:
        try:
            return max(1, int(float(retry_after)))
        except (TypeError, ValueError):
            try:
                retry_at = parsedate_to_datetime(str(retry_after))
                now = datetime.now(retry_at.tzinfo)
                return max(1, int((retry_at - now).total_seconds()))
            except (TypeError, ValueError, OverflowError):
                pass

    response = getattr(error, "response", None)
    text = getattr(response, "text", None)
    if isinstance(text, str) and '"retry_after"' in text:
        marker = '"retry_after":'
        try:
            value = text.split(marker, 1)[1].split(",", 1)[0].split("}", 1)[0].strip()
            return max(1, int(float(value)))
        except (IndexError, TypeError, ValueError):
            pass

    backoff_steps = (5, 15, 30, 60, 120, 300)
    return backoff_steps[min(attempt, len(backoff_steps) - 1)]


async def keep_process_alive() -> None:
    while True:
        await asyncio.sleep(3600)


class BotCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return await global_slash_check(interaction)


class NeonBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="!",
            intents=build_intents(),
            help_command=None,
            activity=discord.Game(name="/help | !help"),
            tree_cls=BotCommandTree,
            max_messages=MESSAGE_CACHE_LIMIT,
            member_cache_flags=build_member_cache_flags(),
            chunk_guilds_at_startup=False,
        )
        self.storage: Storage | None = None
        self.db = None
        self.permissions = default_permissions()
        self.save_permissions = lambda: None
        self.has_synced_commands = False
        self.has_warned_about_message_content = False
        self.token_configured = False
        self.monitor = RuntimeMonitor("Neon Bot")
        self.command_gate = ExecutionGate(COMMAND_CONCURRENCY_LIMIT)
        self.api_gate = ExecutionGate(API_CONCURRENCY_LIMIT)
        self.api_limiter = DiscordApiLimiter(
            self.api_gate,
            self.monitor,
            min_interval=API_MIN_INTERVAL_SECONDS,
        )
        self.public_status_base_url = ""
        self.status_server_started = False
        self.housekeeping_task: asyncio.Task[None] | None = None
        self.command_sync_lock = asyncio.Lock()

    def build_status_snapshot(self) -> dict[str, Any]:
        return self.monitor.build_snapshot(
            bot=self,
            allowed_guild_id=get_allowed_guild_id(),
            commands_synced=self.has_synced_commands,
            token_configured=self.token_configured,
            command_gate=self.command_gate,
            api_gate=self.api_gate,
            public_base_url=self.public_status_base_url,
        )

    async def run_api_call(
        self,
        label: str,
        factory,
        *,
        retries: int = 3,
    ):
        return await self.api_limiter.run(label, factory, retries=retries)

    async def run_storage_call(self, method_name: str, *args, **kwargs):
        if self.storage is None:
            raise RuntimeError("Storage ist nicht initialisiert.")
        method = getattr(self.storage, method_name)
        return await asyncio.to_thread(method, *args, **kwargs)

    async def add_cog(self, cog, /, **kwargs):
        self._instrument_cog(cog)
        return await super().add_cog(cog, **kwargs)

    def _instrument_cog(self, cog: commands.Cog) -> None:
        if getattr(cog, "__neon_instrumented__", False):
            return

        for listener_name, _ in cog.get_listeners():
            listener = getattr(cog, listener_name, None)
            if listener is None or getattr(listener, "__neon_wrapped__", False):
                continue
            setattr(cog, listener_name, self._wrap_listener(cog, listener_name, listener))

        for command in cog.walk_commands():
            self._wrap_command(command)

        for app_command in getattr(cog, "__cog_app_commands__", []):
            self._wrap_app_command(app_command)

        cog.__neon_instrumented__ = True

    def _wrap_listener(self, cog: commands.Cog, listener_name: str, listener):
        @functools.wraps(listener)
        async def wrapped(*args, **kwargs):
            try:
                return await listener(*args, **kwargs)
            except Exception as exc:
                self.monitor.record_event_failed()
                self.monitor.record_issue(
                    f"listener:{cog.__class__.__name__}.{listener_name}",
                    f"Listener-Fehler in {cog.__class__.__name__}.{listener_name}",
                    severity="error",
                    exc=exc,
                )
                return None

        wrapped.__neon_wrapped__ = True
        return wrapped

    def _wrap_command(self, command: commands.Command) -> None:
        if getattr(command, "__neon_wrapped__", False):
            return

        original = command.callback
        command_name = command.qualified_name

        @functools.wraps(original)
        async def wrapped(*args, **kwargs):
            async with self.command_gate.slot():
                self.monitor.record_command_started()
                try:
                    result = await original(*args, **kwargs)
                    self.monitor.record_command_completed()
                    return result
                except Exception as exc:
                    self.monitor.record_command_failed()
                    setattr(exc, "__neon_command_name__", command_name)
                    raise

        command.callback = wrapped
        command.__neon_wrapped__ = True

        app_command = getattr(command, "app_command", None)
        if app_command is not None:
            self._wrap_app_command(app_command, fallback_name=command_name)

    def _wrap_app_command(self, command, *, fallback_name: str | None = None) -> None:
        if getattr(command, "__neon_wrapped__", False):
            return

        original = getattr(command, "_callback", None) or getattr(command, "callback", None)
        if original is None:
            return

        command_name = getattr(command, "qualified_name", None) or fallback_name or getattr(command, "name", "app")

        @functools.wraps(original)
        async def wrapped(*args, **kwargs):
            async with self.command_gate.slot():
                self.monitor.record_command_started()
                try:
                    result = await original(*args, **kwargs)
                    self.monitor.record_command_completed()
                    return result
                except Exception as exc:
                    self.monitor.record_command_failed()
                    setattr(exc, "__neon_command_name__", command_name)
                    raise

        command._callback = wrapped
        try:
            command.callback = wrapped
        except AttributeError:
            pass
        command.__neon_wrapped__ = True


bot = NeonBot()


async def ensure_interaction_response(ctx: commands.Context) -> None:
    interaction = getattr(ctx, "interaction", None)
    if interaction is None or interaction.response.is_done():
        return

    try:
        await ctx.defer()
    except discord.InteractionResponded:
        return
    except discord.HTTPException as exc:
        bot.monitor.record_issue(
            "interaction.defer",
            f"Interaction-Defer fehlgeschlagen: HTTP {exc.status}",
            severity="warning",
            details={"command": getattr(ctx.command, "qualified_name", "unbekannt"), "text": exc.text},
        )


def load_env(path: Path) -> None:
    if not path.exists():
        return

    with path.open("r", encoding="utf-8-sig") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def register_exception_handlers(loop: asyncio.AbstractEventLoop) -> None:
    def loop_exception_handler(_loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        exc = context.get("exception")
        message = context.get("message", "Unbehandelte asyncio-Ausnahme")
        bot.monitor.record_issue(
            "asyncio",
            truncate_message(message),
            severity="error",
            exc=exc if isinstance(exc, BaseException) else None,
            details=None if exc else {"context": truncate_message(context)},
            emit_console=True,
        )

    def sys_exception_handler(exc_type, exc_value, exc_traceback) -> None:
        bot.monitor.record_issue(
            "sys.excepthook",
            f"{exc_type.__name__}: {exc_value}",
            severity="critical",
            details=truncate_message("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)), 4000),
            emit_console=True,
        )

    def thread_exception_handler(args: threading.ExceptHookArgs) -> None:
        bot.monitor.record_issue(
            "threading",
            f"{args.exc_type.__name__}: {args.exc_value}",
            severity="critical",
            details=truncate_message(
                "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)),
                4000,
            ),
            emit_console=True,
        )

    loop.set_exception_handler(loop_exception_handler)
    sys.excepthook = sys_exception_handler
    threading.excepthook = thread_exception_handler


def truncate_message(value: Any, limit: int = 800) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


async def refresh_storage_health() -> None:
    if bot.storage is None:
        bot.monitor.update_storage_health({"configured": False, "ok": False, "error": "Storage nicht initialisiert"})
        return

    try:
        health = await asyncio.to_thread(bot.storage.healthcheck)
        bot.monitor.update_storage_health(health)
    except Exception as exc:
        bot.monitor.record_issue(
            "storage.healthcheck",
            "Storage-Healthcheck fehlgeschlagen",
            severity="warning",
            exc=exc,
        )


async def housekeeping_loop() -> None:
    last_gc_at = 0.0
    last_stats_at = 0.0

    while True:
        try:
            await refresh_storage_health()

            now = asyncio.get_running_loop().time()
            if now - last_gc_at >= MEMORY_CLEANUP_INTERVAL_SECONDS:
                gc.collect()
                last_gc_at = now

            if now - last_stats_at >= STATS_LOG_INTERVAL_SECONDS:
                snapshot = bot.build_status_snapshot()
                log_event(
                    "info",
                    "runtime_stats",
                    status=snapshot["status"],
                    ready=snapshot["ready"],
                    guilds=snapshot["guild_count"],
                    latency_ms=snapshot["latency_ms"],
                    memory_rss_mb=snapshot["memory_rss_mb"],
                    command_queue=snapshot["queues"]["commands"],
                    api_queue=snapshot["queues"]["api"],
                )
                last_stats_at = now
        except Exception as exc:
            bot.monitor.record_issue("housekeeping", "Housekeeping-Loop fehlgeschlagen", severity="warning", exc=exc)

        await asyncio.sleep(STORAGE_HEALTHCHECK_INTERVAL_SECONDS)


async def load_permissions() -> None:
    if bot.storage is None:
        bot.permissions = default_permissions()
        return

    try:
        bot.permissions = await asyncio.to_thread(bot.storage.get_permissions)
    except Exception as exc:
        bot.permissions = default_permissions()
        bot.monitor.record_issue(
            "permissions.load",
            "Permissions konnten nicht geladen werden",
            severity="warning",
            exc=exc,
        )


async def save_permissions_async() -> None:
    if bot.storage is None:
        return

    try:
        await asyncio.to_thread(bot.storage.save_permissions, bot.permissions)
    except Exception as exc:
        bot.monitor.record_issue(
            "permissions.save",
            "Permissions konnten nicht gespeichert werden",
            severity="warning",
            exc=exc,
        )


def schedule_permissions_save() -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        if bot.storage is not None:
            bot.storage.save_permissions(bot.permissions)
        return
    loop.create_task(save_permissions_async())


async def load_cogs() -> None:
    loaded = 0
    failed = 0

    for cog_path in sorted(COGS_DIR.glob("*.py")):
        if cog_path.name.startswith("_"):
            continue

        module_name = f"cogs.{cog_path.stem}"
        try:
            await bot.load_extension(module_name)
            loaded += 1
        except Exception as exc:
            failed += 1
            bot.monitor.record_issue(
                "cog.load",
                f"Cog konnte nicht geladen werden: {module_name}",
                severity="error",
                exc=exc,
                emit_console=True,
            )

    log_event("info", "cogs_loaded", loaded=loaded, failed=failed)


async def reset_bot_runtime() -> None:
    try:
        await bot.http.close()
    except Exception:
        pass
    bot.clear()


@bot.event
async def on_connect() -> None:
    bot.monitor.mark_connect_attempt()


@bot.event
async def on_disconnect() -> None:
    bot.monitor.mark_disconnect()


@bot.event
async def on_resumed() -> None:
    bot.monitor.record_issue(
        "gateway.resume",
        "Gateway-Verbindung wurde erfolgreich fortgesetzt",
        severity="warning",
    )


@bot.event
async def on_ready() -> None:
    try:
        bot.monitor.mark_ready()
        log_event(
            "info",
            "bot_ready",
            user=str(bot.user),
            bot_id=getattr(bot.user, "id", None),
            guilds=len(bot.guilds),
            latency_ms=round(bot.latency * 1000),
        )

        if bot.has_synced_commands:
            return

        async with bot.command_sync_lock:
            if bot.has_synced_commands:
                return
            synced = await bot.run_api_call("tree.sync", lambda: bot.tree.sync(), retries=2)
            bot.has_synced_commands = True
            log_event("info", "slash_sync_complete", command_count=len(synced))
    except Exception as exc:
        bot.monitor.record_issue("event:on_ready", "Fehler in on_ready", severity="error", exc=exc, emit_console=True)


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    try:
        if is_allowed_guild(guild):
            return
        bot.monitor.record_issue(
            "guild.join",
            "Bot wurde einem nicht erlaubten Server hinzugefuegt",
            severity="warning",
            details={"guild": f"{guild} ({guild.id})", "allowed_guild_id": get_allowed_guild_id()},
        )
    except Exception as exc:
        bot.monitor.record_issue("event:on_guild_join", "Fehler in on_guild_join", severity="error", exc=exc)


@bot.before_invoke
async def auto_defer_hybrid_commands(ctx: commands.Context) -> None:
    await ensure_interaction_response(ctx)


@bot.event
async def on_message(message: discord.Message) -> None:
    try:
        if message.author.bot:
            return

        if message.guild and not is_allowed_guild(message.guild):
            return

        if message.guild and not message.content and not bot.has_warned_about_message_content:
            bot.has_warned_about_message_content = True
            bot.monitor.record_issue(
                "message_content",
                "Guild-Nachricht ohne Inhalt empfangen. Message Content Intent vermutlich nicht aktiviert.",
                severity="warning",
            )

        await bot.process_commands(message)
    except Exception as exc:
        bot.monitor.record_issue("event:on_message", "Fehler in on_message", severity="error", exc=exc)


@bot.event
async def on_error(event_method: str, *args, **kwargs) -> None:
    bot.monitor.record_issue(
        f"event:{event_method}",
        f"Unbehandelter Event-Fehler in {event_method}",
        severity="error",
        details=truncate_message(traceback.format_exc(), 4000),
        emit_console=True,
    )


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    command_name = getattr(error, "__neon_command_name__", None)
    if not command_name and isinstance(interaction.data, dict):
        command_name = interaction.data.get("name", "unbekannt")

    if interaction.guild and not is_allowed_guild(interaction.guild):
        message = "❌ Dieser Bot ist nur auf dem freigegebenen Server nutzbar."
    elif isinstance(error, app_commands.MissingPermissions):
        message = "❌ Du hast nicht die nötigen Berechtigungen für diesen Befehl."
    elif isinstance(error, app_commands.CheckFailure):
        message = f"❌ {error}" if str(error) else "❌ Du kannst diesen Befehl nicht benutzen."
    else:
        message = "⚠️ Es ist ein Fehler aufgetreten. Bitte versuche es später erneut."

    root_error = getattr(error, "original", error)
    if not isinstance(error, app_commands.CheckFailure):
        bot.monitor.record_issue(
            "app_command",
            f"Slash-Command fehlgeschlagen: {command_name or 'unbekannt'}",
            severity="error",
            details={
                "guild": f"{interaction.guild} ({interaction.guild.id})" if interaction.guild else "DM",
                "channel": getattr(interaction.channel, "id", None),
                "user": f"{interaction.user} ({interaction.user.id})",
                "command": command_name or "unbekannt",
                "error": format_exception_text(root_error),
            },
        )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        pass


@bot.check
async def global_check(ctx: commands.Context) -> bool:
    if ctx.guild and not is_allowed_guild(ctx.guild):
        raise commands.CheckFailure("Dieser Bot ist nur auf dem freigegebenen Server nutzbar.")

    if ctx.author.id in bot.permissions.get("owner", []):
        return True

    if ctx.guild and ctx.guild.id in bot.permissions.get("banned_servers", []):
        if ctx.command and ctx.command.name != "help":
            owner = ctx.guild.owner
            if owner:
                try:
                    embed = discord.Embed(
                        title="Server gesperrt",
                        description=f"Dein Server {ctx.guild.name} ist gesperrt. Commands sind deaktiviert außer help.",
                        color=discord.Color.red(),
                    )
                    await owner.send(embed=embed)
                except Exception:
                    pass
            return False

    if ctx.author.id in bot.permissions.get("banned_users", []):
        if ctx.command and ctx.command.name != "help":
            try:
                embed = discord.Embed(
                    title="User gesperrt",
                    description="Du bist gesperrt. Commands sind deaktiviert außer help.",
                    color=discord.Color.red(),
                )
                await ctx.author.send(embed=embed)
            except Exception:
                pass
            return False

    return True


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Du hast nicht die nötigen Berechtigungen für diesen Befehl.")
        return
    if isinstance(error, commands.CheckFailure):
        message = f"❌ {error}" if str(error) else "❌ Du kannst diesen Befehl nicht benutzen."
        await ctx.send(message)
        return
    if isinstance(error, commands.UserInputError):
        await ctx.send(f"❌ Eingabefehler: {error}")
        return

    root_error = getattr(error, "original", error)
    command_name = getattr(ctx.command, "qualified_name", "unbekannt")
    bot.monitor.record_issue(
        "prefix_command",
        f"Command fehlgeschlagen: {command_name}",
        severity="error",
        details={
            "guild": f"{ctx.guild} ({ctx.guild.id})" if ctx.guild else "DM",
            "channel": getattr(ctx.channel, "id", None),
            "user": f"{ctx.author} ({ctx.author.id})",
            "command": command_name,
            "error": format_exception_text(root_error),
        },
    )

    try:
        await ctx.send("⚠️ Es ist ein Fehler aufgetreten. Bitte versuche es später erneut.")
    except Exception:
        pass


async def global_slash_check(interaction: discord.Interaction) -> bool:
    if interaction.guild and not is_allowed_guild(interaction.guild):
        raise app_commands.CheckFailure("Dieser Bot ist nur auf dem freigegebenen Server nutzbar.")

    permissions = getattr(interaction.client, "permissions", {})
    if interaction.user.id in permissions.get("owner", []):
        return True

    command_name = interaction.command.qualified_name if interaction.command else None

    if interaction.guild and interaction.guild.id in permissions.get("banned_servers", []):
        if command_name != "help":
            owner = interaction.guild.owner
            if owner:
                try:
                    embed = discord.Embed(
                        title="Server gesperrt",
                        description=f"Dein Server {interaction.guild.name} ist gesperrt. Commands sind deaktiviert außer help.",
                        color=discord.Color.red(),
                    )
                    await owner.send(embed=embed)
                except Exception:
                    pass
            raise app_commands.CheckFailure("Server gesperrt")

    if interaction.user.id in permissions.get("banned_users", []):
        if command_name != "help":
            try:
                embed = discord.Embed(
                    title="User gesperrt",
                    description="Du bist gesperrt. Commands sind deaktiviert außer help.",
                    color=discord.Color.red(),
                )
                await interaction.user.send(embed=embed)
            except Exception:
                pass
            raise app_commands.CheckFailure("User gesperrt")

    return True


async def run_bot_forever(token: str) -> None:
    attempt = 0

    while True:
        bot.monitor.mark_connect_attempt()
        try:
            await bot.start(token)
            bot.monitor.mark_restart()
            bot.monitor.record_issue(
                "gateway",
                "Bot-Session wurde geschlossen. Neuer Start wird vorbereitet.",
                severity="warning",
            )
            await reset_bot_runtime()
            await asyncio.sleep(5)
            attempt = 0
        except discord.LoginFailure as exc:
            bot.monitor.record_issue(
                "startup",
                "Bot konnte nicht online gehen: Ungueltiges Discord-Token oder App-Zugang verweigert.",
                severity="critical",
                exc=exc,
                emit_console=True,
            )
            bot.monitor.set_login_state("config_error")
            await reset_bot_runtime()
            await asyncio.sleep(300)
        except discord.HTTPException as exc:
            delay = get_retry_after(exc, attempt)
            bot.monitor.record_issue(
                "startup",
                f"Bot konnte nicht online gehen: Discord HTTP {exc.status}. Neuer Versuch in {delay}s.",
                severity="error" if exc.status != 429 else "warning",
                exc=exc,
                emit_console=True,
            )
            bot.monitor.mark_restart()
            await reset_bot_runtime()
            await asyncio.sleep(delay)
            attempt += 1
        except (OSError, asyncio.TimeoutError) as exc:
            delay = min(300, 15 * (attempt + 1))
            bot.monitor.record_issue(
                "startup",
                f"Bot konnte nicht online gehen: Netzwerkfehler. Neuer Versuch in {delay}s.",
                severity="warning",
                exc=exc,
                emit_console=True,
            )
            bot.monitor.mark_restart()
            await reset_bot_runtime()
            await asyncio.sleep(delay)
            attempt += 1
        except Exception as exc:
            delay = min(300, 30 * (attempt + 1))
            bot.monitor.record_issue(
                "startup",
                f"Bot konnte nicht online gehen: {type(exc).__name__}. Neuer Versuch in {delay}s.",
                severity="error",
                exc=exc,
                emit_console=True,
            )
            bot.monitor.mark_restart()
            await reset_bot_runtime()
            await asyncio.sleep(delay)
            attempt += 1


async def main() -> None:
    load_dotenv(BASE_DIR / ".env")
    load_env(BASE_DIR / ".env")

    bot.public_status_base_url = get_public_status_base_url()
    bot.token_configured = bool((os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN") or "").strip())

    loop = asyncio.get_running_loop()
    register_exception_handlers(loop)

    port = get_status_port()
    start_status_server(port=port, snapshot_factory=bot.build_status_snapshot)
    bot.monitor.mark_health_server(port)
    bot.status_server_started = True
    log_event("info", "status_server_started", port=port, status_page=f"{bot.public_status_base_url}/status")

    bot.storage = Storage()
    await load_permissions()
    bot.save_permissions = schedule_permissions_save

    if bot.housekeeping_task is None or bot.housekeeping_task.done():
        bot.housekeeping_task = asyncio.create_task(housekeeping_loop(), name="housekeeping")

    token = (os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN") or "").strip()
    if not token:
        bot.monitor.set_login_state("config_error")
        bot.monitor.record_issue(
            "startup",
            "Bot konnte nicht online gehen: DISCORD_TOKEN oder TOKEN fehlt in den Render-Environment-Variablen.",
            severity="critical",
            emit_console=True,
        )
        await keep_process_alive()
        return

    await load_cogs()
    await refresh_storage_health()
    log_event(
        "info",
        "startup",
        python=sys.version.split()[0],
        discord_py=discord.__version__,
        message_cache=MESSAGE_CACHE_LIMIT,
        command_concurrency=COMMAND_CONCURRENCY_LIMIT,
        api_concurrency=API_CONCURRENCY_LIMIT,
    )
    await run_bot_forever(token)


if __name__ == "__main__":
    asyncio.run(main())
