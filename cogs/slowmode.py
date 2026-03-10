import discord
from discord.ext import commands
import datetime

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slowmode", description="Befehl slowmode")\n    async def slowmode(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Slowmode(bot))