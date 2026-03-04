import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Fix: Lädt Cogs auch aus Unterordnern
        cogs_path = Path(__file__).parent / "cogs"
        for path in cogs_path.rglob("*.py"):
            if not path.name.startswith("__"):
                # Umwandlung von Pfad zu Modul-Punkt-Notation
                relative_path = path.relative_to(Path(__file__).parent)
                module_name = f"bot.{str(relative_path).replace(os.sep, '.')[:-3]}"
                try:
                    await self.load_extension(module_name)
                    print(f"✅ Geladen: {module_name}")
                except Exception as e:
                    print(f"❌ Fehler bei {module_name}: {e}")

bot = NeonBot()
bot.run(os.getenv("DISCORD_TOKEN"))
