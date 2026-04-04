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

bot = commands.Bot(command_prefix="!", intents=INTENTS, help_command=None, activity=discord.Game(name="/help | !help"))
bot.storage = Storage()

# Lade Permissions von Supabase
bot.permissions = bot.storage.get_permissions()
bot.save_permissions = lambda: bot.storage.save_permissions(bot.permissions)


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


def load_env(path: Path) -> None:
    if not path.exists():
        return

    with path.open("r", encoding="utf-8") as env_file:
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
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} Slash-Befehle synchronisiert.")
    except Exception as exc:
        print("Fehler beim Synchronisieren der Slash-Befehle:", exc, file=sys.stderr)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ Du hast nicht die nötigen Berechtigungen für diesen Befehl."
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


@bot.tree.interaction_check
async def global_slash_check(interaction):
    guild = interaction.guild
    cmd_name = interaction.command.name if interaction.command else None

    if guild and guild.id in bot.permissions.get("banned_servers", []):
        if cmd_name not in ["help"]:
            owner = guild.owner
            if owner:
                try:
                    embed = discord.Embed(title="Server gesperrt", description=f"Dein Server {guild.name} ist gesperrt. Commands sind deaktiviert außer help.", color=discord.Color.red())
                    await owner.send(embed=embed)
                except:
                    pass
            return False

    if interaction.user.id in bot.permissions.get("banned_users", []):
        if cmd_name not in ["help"]:
            try:
                embed = discord.Embed(title="User gesperrt", description="Du bist gesperrt. Commands sind deaktiviert außer help.", color=discord.Color.red())
                await interaction.user.send(embed=embed)
            except:
                pass
            return False
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
                continue

            result = setup(bot)
            if inspect.isawaitable(result):
                await result

            print(f"Cog geladen: {module_name}")
        except Exception as exc:
            print(f"Fehler beim Laden von {module_name}: {exc}", file=sys.stderr)


async def main() -> None:
    # Lade .env Datei
    load_dotenv(BASE_DIR / ".env")
    load_env(BASE_DIR / ".env")
    
    token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
    if not token:
        raise RuntimeError(
            "Kein Discord-Token gefunden. Bitte lege DISCORD_TOKEN oder TOKEN in der .env-Datei an."
        )

    start_health_server()
    await load_cogs()
    await bot.start(token)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
