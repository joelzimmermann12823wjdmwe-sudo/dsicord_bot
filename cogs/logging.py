import discord
from discord.ext import commands
import datetime

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="logging", description="Befehl logging")\n    async def logging(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Logging(bot))