import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class NeonBot(commands.Bot):
    def __init__(self):
        # BUGFIX: Alle Intents aktivieren, damit Moderation & Member Tracking klappt!
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        print("Lade Cogs...")
        if os.path.exists("./cogs"):
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        print(f"✅ {filename} geladen")
                    except Exception as e:
                        print(f"❌ Fehler bei {filename}: {e}")
        try:
            await self.tree.sync()
            print("✅ Slash-Commands synchronisiert!")
        except Exception as e:
            print(f"❌ Sync-Fehler: {e}")

    async def on_ready(self):
        print(f"✅ Bot {self.user} ist ONLINE!")

async def main():
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())