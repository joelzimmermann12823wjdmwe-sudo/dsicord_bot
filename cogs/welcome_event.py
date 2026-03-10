import discord
from discord.ext import commands
import datetime

class Welcomeevent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="welcome_event", description="Befehl welcome_event")\n    async def welcome_event(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Welcomeevent(bot))