import discord
from discord.ext import commands
import datetime

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="automod", description="Befehl automod")\n    async def automod(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Automod(bot))