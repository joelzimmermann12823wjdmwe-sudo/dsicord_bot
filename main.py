import asyncio
import json
import inspect
import os
import sys
import threading
import traceback
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib import import_module
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from storage import Storage

BASE_DIR = Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True
INTENTS.message_content = True

class BotCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        data = interaction.data if isinstance(interaction.data, dict) else {}
        command_name = data.get("name", "<unbekannt>")
        user = interaction.user
        print(f"Slash-Command empfangen: /{command_name} von {user} ({user.id})")
        return await global_slash_check(interaction)


bot = commands.Bot(
    command_prefix="!",
    intents=INTENTS,
    help_command=None,
    activity=discord.Game(name="/help | !help"),
    tree_cls=BotCommandTree,
)
bot.storage = None
bot.db = None
bot.permissions = {"owner": [], "admins": [], "developers": [], "banned_servers": [], "banned_users": []}
bot.save_permissions = lambda: None
bot.has_synced_commands = False
bot.has_checked_application_config = False
bot.has_warned_about_message_content = False
bot.status_reporter_ready = False
bot.started_at = datetime.now().astimezone()


def get_int_env(name: str) -> int | None:
    value = (os.getenv(name) or "").strip()
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        print(f"Ungültige ID in {name}: {value}", file=sys.stderr)
        return None


def get_allowed_guild_id() -> int | None:
    return get_int_env("ALLOWED_GUILD_ID")


def get_status_dm_user_id() -> int | None:
    return get_int_env("STATUS_DM_USER_ID")


def get_status_channel_id() -> int | None:
    return get_int_env("STATUS_CHANNEL_ID")


def get_status_role_id() -> int | None:
    return get_int_env("STATUS_ROLE_ID")


def is_internal_owner(user_id: int) -> bool:
    return user_id in bot.permissions.get("owner", [])


def is_allowed_guild(guild: discord.abc.Snowflake | None) -> bool:
    allowed_guild_id = get_allowed_guild_id()
    if allowed_guild_id is None or guild is None:
        return True
    return guild.id == allowed_guild_id


def format_exception_text(error: BaseException) -> str:
    return "".join(traceback.format_exception_only(type(error), error)).strip()[:1000]


def get_health_snapshot() -> dict[str, Any]:
    now = datetime.now().astimezone()
    allowed_guild_id = get_allowed_guild_id()
    connected_guilds = len(bot.guilds)
    allowed_guild_connected = (
        True if allowed_guild_id is None else any(guild.id == allowed_guild_id for guild in bot.guilds)
    )
    storage_health = bot.storage.healthcheck() if bot.storage is not None else {"configured": False, "ok": False}

    checks = {
        "bot_user_available": bot.user is not None,
        "discord_ready": bot.is_ready(),
        "commands_synced": bot.has_synced_commands,
        "allowed_guild_connected": allowed_guild_connected,
        "status_channel_configured": get_status_channel_id() is not None,
        "status_dm_configured": get_status_dm_user_id() is not None,
        "storage_initialized": bot.storage is not None,
        "database_connected": bool(storage_health.get("ok")),
    }

    ready = checks["discord_ready"] and checks["storage_initialized"] and checks["database_connected"]
    if allowed_guild_id is not None:
        ready = ready and checks["allowed_guild_connected"]

    if all(checks.values()):
        severity = "ok"
    elif ready:
        severity = "degraded"
    else:
        severity = "error"

    return {
        "status": severity,
        "ready": ready,
        "bot_user": str(bot.user) if bot.user else None,
        "bot_id": getattr(bot.user, "id", None),
        "latency_ms": round(bot.latency * 1000) if bot.user else None,
        "guild_count": connected_guilds,
        "user_count": len(bot.users),
        "allowed_guild_id": allowed_guild_id,
        "started_at": bot.started_at.isoformat(),
        "uptime_seconds": int((now - bot.started_at).total_seconds()),
        "checks": checks,
        "database": storage_health,
    }


def send_json_response(handler: BaseHTTPRequestHandler, status_code: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=True, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def build_health_html(snapshot: dict[str, Any]) -> str:
    color_map = {"ok": "#16a34a", "degraded": "#d97706", "error": "#dc2626"}
    status_color = color_map.get(snapshot["status"], "#2563eb")
    checks_html = "".join(
        (
            "<li><strong>{name}</strong>: {value}</li>".format(
                name=key.replace("_", " ").title(),
                value="OK" if value else "Fehlt",
            )
        )
        for key, value in snapshot["checks"].items()
    )

    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Neon Bot Health</title>
  <style>
    :root {{ color-scheme: light; }}
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: linear-gradient(135deg, #0f172a, #1e293b); color: #e2e8f0; }}
    main {{ max-width: 760px; margin: 40px auto; padding: 24px; }}
    .card {{ background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 18px; padding: 24px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25); }}
    .badge {{ display: inline-block; padding: 8px 14px; border-radius: 999px; background: {status_color}; color: white; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }}
    h1 {{ margin: 16px 0 8px; font-size: 2rem; }}
    p, li {{ color: #cbd5e1; line-height: 1.5; }}
    ul {{ padding-left: 20px; }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 20px 0; }}
    .meta div {{ background: rgba(30, 41, 59, 0.85); padding: 14px; border-radius: 12px; }}
    code {{ color: #93c5fd; }}
    a {{ color: #67e8f9; }}
  </style>
</head>
<body>
  <main>
    <section class="card">
      <span class="badge">{snapshot["status"]}</span>
      <h1>Neon Bot Healthcheck</h1>
      <p>Browser-Seite fuer deinen Bot- und Website-Status.</p>
      <div class="meta">
        <div><strong>Ready</strong><br>{snapshot["ready"]}</div>
        <div><strong>Bot</strong><br>{snapshot["bot_user"] or "offline"}</div>
        <div><strong>Guilds</strong><br>{snapshot["guild_count"]}</div>
        <div><strong>Latency</strong><br>{snapshot["latency_ms"] if snapshot["latency_ms"] is not None else "-"} ms</div>
        <div><strong>Uptime</strong><br>{snapshot["uptime_seconds"]}s</div>
        <div><strong>Allowed Guild</strong><br>{snapshot["allowed_guild_id"] or "nicht gesetzt"}</div>
        <div><strong>Database</strong><br>{"verbunden" if snapshot["database"].get("ok") else "fehlerhaft"}</div>
      </div>
      <p>JSON-Endpunkte: <code>/health</code>, <code>/health/live</code>, <code>/health/ready</code>, <code>/health/details</code></p>
      <ul>{checks_html}</ul>
    </section>
  </main>
</body>
</html>"""


def build_status_embed(
    title: str,
    description: str,
    *,
    color: discord.Color,
    details: dict[str, Any] | None = None,
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.timestamp = discord.utils.utcnow()

    for name, value in (details or {}).items():
        if value is None:
            continue
        text = str(value)
        if not text:
            continue
        embed.add_field(name=name, value=text[:1024], inline=False)

    return embed


async def send_status_report(
    title: str,
    description: str,
    *,
    color: discord.Color = discord.Color.orange(),
    details: dict[str, Any] | None = None,
    ping_role: bool = False,
) -> None:
    if not bot.is_ready():
        return

    embed = build_status_embed(title, description, color=color, details=details)
    allowed_mentions = discord.AllowedMentions.none()

    dm_user_id = get_status_dm_user_id()
    if dm_user_id:
        user = bot.get_user(dm_user_id)
        if user is None:
            try:
                user = await bot.fetch_user(dm_user_id)
            except Exception:
                user = None

        if user is not None:
            try:
                await user.send(embed=embed)
            except Exception:
                pass

    channel_id = get_status_channel_id()
    if not channel_id:
        return

    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            fetched_channel = await bot.fetch_channel(channel_id)
            channel = fetched_channel if isinstance(fetched_channel, discord.abc.Messageable) else None
        except Exception:
            channel = None

    if channel is None:
        return

    content = None
    role_id = get_status_role_id()
    if ping_role and role_id:
        content = f"<@&{role_id}>"
        allowed_mentions = discord.AllowedMentions(roles=True)

    try:
        await channel.send(content=content, embed=embed, allowed_mentions=allowed_mentions)
    except Exception:
        pass


bot.send_status_report = send_status_report


async def ensure_interaction_response(ctx: commands.Context) -> None:
    interaction = getattr(ctx, "interaction", None)
    if interaction is None or interaction.response.is_done():
        return

    try:
        await ctx.defer()
    except discord.InteractionResponded:
        return
    except discord.HTTPException as exc:
        command_name = getattr(ctx.command, "qualified_name", "<unbekannt>")
        print(
            f"Interaction-Defer fehlgeschlagen fuer {command_name}: "
            f"HTTP {exc.status} / Code {exc.code} / {exc.text}",
            file=sys.stderr,
        )


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        snapshot = get_health_snapshot()

        if self.path in ("/", "/healthz", "/health"):
            send_json_response(self, 200, snapshot)
            return

        if self.path == "/health/live":
            send_json_response(
                self,
                200,
                {
                    "status": "ok",
                    "alive": True,
                    "started_at": snapshot["started_at"],
                    "uptime_seconds": snapshot["uptime_seconds"],
                },
            )
            return

        if self.path == "/health/ready":
            send_json_response(self, 200 if snapshot["ready"] else 503, snapshot)
            return

        if self.path == "/health/details":
            send_json_response(self, 200 if snapshot["status"] != "error" else 503, snapshot)
            return

        if self.path == "/status" or self.path == "/health/ui":
            body = build_health_html(snapshot).encode("utf-8")
            self.send_response(200 if snapshot["status"] != "error" else 503)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        send_json_response(
            self,
            404,
            {
                "status": "not_found",
                "message": "Verfuegbare Routen: /health, /health/live, /health/ready, /health/details, /status",
            },
        )

    def log_message(self, format, *args):
        return


def start_health_server() -> None:
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Health server listening on port {port}")


def print_startup_diagnostics() -> None:
    print("Startup-Diagnose:", file=sys.stderr)
    for key in ("DISCORD_TOKEN", "TOKEN", "SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY", "PORT"):
        status = "gesetzt" if os.getenv(key) else "fehlt"
        print(f"  {key}: {status}", file=sys.stderr)


def load_env(path: Path) -> None:
    if not path.exists():
        return

    with path.open("r", encoding="utf-8-sig") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


@bot.event
async def on_ready() -> None:
    print(f"Bot ist online als {bot.user} ({bot.user.id})")

    if not bot.status_reporter_ready:
        bot.status_reporter_ready = True
        allowed_guild_id = get_allowed_guild_id()
        await send_status_report(
            "Bot Online",
            "Der Bot ist erfolgreich gestartet und einsatzbereit.",
            color=discord.Color.green(),
            details={
                "Bot": f"{bot.user} ({bot.user.id})",
                "Erlaubter Server": allowed_guild_id or "nicht gesetzt",
                "Serveranzahl": len(bot.guilds),
            },
            ping_role=True,
        )

    if not bot.has_checked_application_config:
        try:
            app_info = await bot.application_info()
            endpoint_url = getattr(app_info, "interactions_endpoint_url", None)
            if endpoint_url:
                print(
                    "WARNUNG: In den Discord Developer Portal Settings ist eine "
                    f"Interactions Endpoint URL gesetzt: {endpoint_url}. "
                    "Dann kommen Slash-Commands nicht ueber den Gateway bei discord.py an.",
                    file=sys.stderr,
                )
            else:
                print("Interactions werden ueber den Gateway empfangen.")
        except Exception as exc:
            print(f"Anwendungs-Konfiguration konnte nicht geprueft werden: {exc}", file=sys.stderr)
        finally:
            bot.has_checked_application_config = True

    if bot.has_synced_commands:
        return

    try:
        synced = await bot.tree.sync()
        bot.has_synced_commands = True
        print(f"{len(synced)} Slash-Befehle synchronisiert.")
    except Exception as exc:
        print("Fehler beim Synchronisieren der Slash-Befehle:", exc, file=sys.stderr)


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    if is_allowed_guild(guild):
        await send_status_report(
            "Bot Server-Beitritt",
            "Der Bot wurde dem erlaubten Server hinzugefuegt.",
            color=discord.Color.green(),
            details={"Server": f"{guild} ({guild.id})"},
            ping_role=True,
        )
        return

    print(
        f"Bot wurde einem nicht erlaubten Server hinzugefuegt: {guild} ({guild.id})",
        file=sys.stderr,
    )
    await send_status_report(
        "Nicht erlaubter Server",
        "Der Bot wurde einem nicht freigegebenen Server hinzugefuegt.",
        color=discord.Color.orange(),
        details={"Server": f"{guild} ({guild.id})", "Erlaubter Server": get_allowed_guild_id()},
        ping_role=True,
    )


@bot.before_invoke
async def auto_defer_hybrid_commands(ctx: commands.Context) -> None:
    print(f"Command wird ausgefuehrt: {ctx.command} von {ctx.author} ({ctx.author.id})")
    await ensure_interaction_response(ctx)


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if message.guild and not is_allowed_guild(message.guild):
        return

    if message.guild and not message.content and not bot.has_warned_about_message_content:
        print(
            "WARNUNG: Guild-Nachricht ohne Inhalt empfangen. "
            "Message Content Intent ist im Discord Developer Portal wahrscheinlich nicht aktiviert.",
            file=sys.stderr,
        )
        bot.has_warned_about_message_content = True

    if message.content.startswith("!"):
        print(f"Prefix-Command empfangen: {message.content.split()[0]} von {message.author} ({message.author.id})")

    await bot.process_commands(message)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if interaction.guild and not is_allowed_guild(interaction.guild):
        message = "❌ Dieser Bot ist nur auf dem freigegebenen Server nutzbar."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except Exception:
            pass
        return

    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ Du hast nicht die nötigen Berechtigungen für diesen Befehl."
    elif isinstance(error, app_commands.CheckFailure):
        message = f"❌ {error}" if str(error) else "❌ Du kannst diesen Befehl nicht benutzen."
    else:
        message = "⚠️ Es ist ein Fehler aufgetreten. Bitte versuche es später erneut."

    print("App-Command-Fehler:", file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    await send_status_report(
        "App-Command-Fehler",
        "Bei einem Slash-Command ist ein Fehler aufgetreten.",
        color=discord.Color.red(),
        details={
            "Server": f"{interaction.guild} ({interaction.guild.id})" if interaction.guild else "DM",
            "Kanal": getattr(interaction.channel, "mention", "unbekannt"),
            "User": f"{interaction.user} ({interaction.user.id})",
            "Command": (interaction.data or {}).get("name", "unbekannt") if isinstance(interaction.data, dict) else "unbekannt",
            "Fehler": format_exception_text(error),
        },
        ping_role=True,
    )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        pass


@bot.check
async def global_check(ctx):
    if ctx.guild and not is_allowed_guild(ctx.guild):
        raise commands.CheckFailure("Dieser Bot ist nur auf dem freigegebenen Server nutzbar.")

    if is_internal_owner(ctx.author.id):
        return True

    # Check banned servers
    if ctx.guild and ctx.guild.id in bot.permissions.get("banned_servers", []):
        if ctx.command and ctx.command.name not in ["help"]:
            # Nachricht an owner
            owner = ctx.guild.owner
            if owner:
                try:
                    embed = discord.Embed(title="Server gesperrt", description=f"Dein Server {ctx.guild.name} ist gesperrt. Commands sind deaktiviert außer help.", color=discord.Color.red())
                    await owner.send(embed=embed)
                except:
                    pass
            return False
    # Check banned users
    if ctx.author.id in bot.permissions.get("banned_users", []):
        if ctx.command and ctx.command.name not in ["help"]:
            try:
                embed = discord.Embed(title="User gesperrt", description="Du bist gesperrt. Commands sind deaktiviert außer help.", color=discord.Color.red())
                await ctx.author.send(embed=embed)
            except:
                pass
            return False
    return True


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
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
        await ctx.send(f"❌ Eingabefehler: {str(error)}")
        return

    print("Command-Fehler:", file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    await send_status_report(
        "Command-Fehler",
        "Bei einem Prefix- oder Hybrid-Command ist ein Fehler aufgetreten.",
        color=discord.Color.red(),
        details={
            "Server": f"{ctx.guild} ({ctx.guild.id})" if ctx.guild else "DM",
            "Kanal": getattr(ctx.channel, "mention", "unbekannt"),
            "User": f"{ctx.author} ({ctx.author.id})",
            "Command": getattr(ctx.command, "qualified_name", "unbekannt"),
            "Fehler": format_exception_text(error),
        },
        ping_role=True,
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

    guild = interaction.guild
    data = interaction.data if isinstance(interaction.data, dict) else {}
    cmd_name = data.get("name")

    if guild and guild.id in permissions.get("banned_servers", []):
        if cmd_name != "help":
            owner = guild.owner
            if owner:
                try:
                    embed = discord.Embed(title="Server gesperrt", description=f"Dein Server {guild.name} ist gesperrt. Commands sind deaktiviert außer help.", color=discord.Color.red())
                    await owner.send(embed=embed)
                except Exception:
                    pass
            raise app_commands.CheckFailure("Server gesperrt")

    if interaction.user.id in permissions.get("banned_users", []):
        if cmd_name != "help":
            try:
                embed = discord.Embed(title="User gesperrt", description="Du bist gesperrt. Commands sind deaktiviert außer help.", color=discord.Color.red())
                await interaction.user.send(embed=embed)
            except Exception:
                pass
            raise app_commands.CheckFailure("User gesperrt")
    return True


async def load_cogs() -> None:
    for cog_path in sorted(COGS_DIR.glob("*.py")):
        if cog_path.name.startswith("_"):
            continue

        module_name = f"cogs.{cog_path.stem}"
        try:
            module = import_module(module_name)
            setup = getattr(module, "setup", None)
            if setup is None:
                print(f"Cog übersprungen: {module_name} (keine setup-Funktion gefunden)", file=sys.stderr)
                continue

            result = setup(bot)
            if inspect.isawaitable(result):
                await result

            print(f"Cog geladen: {module_name}")
        except Exception as exc:
            print(f"Fehler beim Laden von {module_name}: {exc}", file=sys.stderr)


def format_retry_delay(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def get_discord_retry_delay(error: discord.HTTPException, attempt: int) -> int:
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

    response_data = getattr(error, "response", None)
    if response_data is not None:
        text = getattr(response_data, "text", None)
        if isinstance(text, str) and '"retry_after"' in text:
            marker = '"retry_after":'
            try:
                value = text.split(marker, 1)[1].split(",", 1)[0].split("}", 1)[0].strip()
                return max(1, int(float(value)))
            except (IndexError, TypeError, ValueError):
                pass

    backoff_steps = (60, 120, 300, 600, 900)
    return backoff_steps[min(attempt, len(backoff_steps) - 1)]


async def reset_bot_after_login_failure() -> None:
    try:
        # Nach einem 429 beim statischen Login existiert noch keine aktive
        # Gateway-Verbindung. Ein volles bot.close() setzt den internen
        # Loop-Zustand auf MISSING und kann den naechsten Startversuch brechen.
        await bot.http.close()
    except Exception:
        pass
    bot.clear()


async def start_bot_with_retry(token: str) -> None:
    attempt = 0

    while True:
        try:
            await bot.start(token)
            return
        except discord.LoginFailure:
            raise
        except discord.HTTPException as exc:
            if exc.status != 429:
                raise

            delay = get_discord_retry_delay(exc, attempt)
            retry_time = datetime.now().astimezone() + timedelta(seconds=delay)
            print(
                "Discord-Login wurde mit HTTP 429 begrenzt. "
                f"Nächster Versuch in {delay} Sekunden "
                f"({format_retry_delay(delay)}) um {retry_time.strftime('%Y-%m-%d %H:%M:%S %Z')}.",
                file=sys.stderr,
            )
            await reset_bot_after_login_failure()
            await asyncio.sleep(delay)
            attempt += 1


async def main() -> None:
    # Lade .env Datei
    load_dotenv(BASE_DIR / ".env")
    load_env(BASE_DIR / ".env")

    token = (os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN") or "").strip()
    if not token:
        raise RuntimeError(
            "Kein Discord-Token gefunden. Setze DISCORD_TOKEN oder TOKEN lokal in .env "
            "und auf Render unter Environment."
        )

    bot.storage = Storage()
    bot.permissions = bot.storage.get_permissions()
    bot.save_permissions = lambda: bot.storage.save_permissions(bot.permissions)

    start_health_server()
    await load_cogs()
    await start_bot_with_retry(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"Fataler Startfehler: {exc}", file=sys.stderr)
        print_startup_diagnostics()
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
        sys.exit(1)
