import asyncio
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


def is_internal_owner(user_id: int) -> bool:
    return user_id in bot.permissions.get("owner", [])


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
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

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


@bot.before_invoke
async def auto_defer_hybrid_commands(ctx: commands.Context) -> None:
    print(f"Command wird ausgefuehrt: {ctx.command} von {ctx.author} ({ctx.author.id})")
    await ensure_interaction_response(ctx)


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
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
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ Du hast nicht die nötigen Berechtigungen für diesen Befehl."
    elif isinstance(error, app_commands.CheckFailure):
        message = f"❌ {error}" if str(error) else "❌ Du kannst diesen Befehl nicht benutzen."
    else:
        message = "⚠️ Es ist ein Fehler aufgetreten. Bitte versuche es später erneut."

    print("App-Command-Fehler:", file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        pass


@bot.check
async def global_check(ctx):
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
    try:
        await ctx.send("⚠️ Es ist ein Fehler aufgetreten. Bitte versuche es später erneut.")
    except Exception:
        pass


async def global_slash_check(interaction: discord.Interaction) -> bool:
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
