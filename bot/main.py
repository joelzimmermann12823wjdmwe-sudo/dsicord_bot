import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Automatisch alle Dateien im cogs-Ordner laden
        for filename in os.listdir('./bot/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'bot.cogs.{filename[:-3]}')
                print(f'✅ Modul geladen: {filename}')

    async def on_ready(self):
        print(f'🚀 {self.user} ist bereit und steuert 50+ Befehle!')

bot = NeonBot()
bot.run(os.getenv("DISCORD_TOKEN"))
