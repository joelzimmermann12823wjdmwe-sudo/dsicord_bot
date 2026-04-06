import asyncio
import inspect
import os
import sys
import threading
import traceback
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


def is_internal_owner(user_id: int) -> bool:
    return user_id in bot.permissions.get("owner", [])


async def ensure_interaction_response(ctx: commands.Context) -> None:
    interaction = getattr(ctx, "interaction", None)
    if interaction is None or interaction.response.is_done():
        return

    try:
        await ctx.defer()
    except (discord.HTTPException, discord.InteractionResponded):
        pass


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
    await ensure_interaction_response(ctx)

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


def get_discord_retry_delay(error: discord.HTTPException, attempt: int) -> int:
    headers = getattr(error.response, "headers", {}) or {}
    retry_after = headers.get("Retry-After")
    if retry_after:
        try:
            return max(1, int(float(retry_after)))
        except (TypeError, ValueError):
            pass

    backoff_steps = (60, 120, 300, 600, 900)
    return backoff_steps[min(attempt, len(backoff_steps) - 1)]


async def reset_bot_after_login_failure() -> None:
    try:
        await bot.close()
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
            print(
                "Discord-Login wurde mit HTTP 429 begrenzt. "
                f"Nächster Versuch in {delay} Sekunden.",
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
