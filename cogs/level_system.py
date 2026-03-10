import discord
from discord.ext import commands
import datetime
import asyncio

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg): # XP Logik hier
        pass

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))