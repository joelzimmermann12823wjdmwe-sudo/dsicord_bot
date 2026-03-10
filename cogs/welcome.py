import discord
from discord.ext import commands
import datetime

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="welcome", description="Befehl welcome")\n    async def welcome(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Welcome(bot))