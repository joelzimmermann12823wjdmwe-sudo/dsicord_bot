import discord
from discord.ext import commands
import datetime
import asyncio

class LoggingEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, b, a): pass

async def setup(bot):
    await bot.add_cog(LoggingEvent(bot))