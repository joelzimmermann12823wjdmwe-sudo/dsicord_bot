import discord
from discord.ext import commands
import datetime

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return
        # Platzhalter für Datenbank-Logik
        pass

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))