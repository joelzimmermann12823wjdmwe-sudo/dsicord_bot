import discord
from discord.ext import commands
import datetime

class LoggingEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        pass

async def setup(bot):
    await bot.add_cog(LoggingEvent(bot))