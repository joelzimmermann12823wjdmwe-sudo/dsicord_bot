import inspect
import os
import sys
from importlib import import_module
from pathlib import Path

import discord
from discord.ext import commands

from storage import Storage

BASE_DIR = Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True
INTENTS.message_content = True

bot = commands.Bot(command_prefix="!", intents=INTENTS, help_command=None)
bot.storage = Storage(BASE_DIR / "storage.bin")


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
    load_env(BASE_DIR / ".env")
    token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
    if not token:
        raise RuntimeError(
            "Kein Discord-Token gefunden. Bitte lege DISCORD_TOKEN oder TOKEN in der .env-Datei an."
        )

    await load_cogs()
    await bot.start(token)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
