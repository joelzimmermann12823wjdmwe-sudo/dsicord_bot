import discord
from discord.ext import commands
import datetime

class Loggingevent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="logging_event", description="Befehl logging_event")\n    async def logging_event(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Loggingevent(bot))