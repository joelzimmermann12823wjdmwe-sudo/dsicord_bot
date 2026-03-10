import discord
from discord.ext import commands
import datetime

class Linkfilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="link_filter", description="Befehl link_filter")\n    async def link_filter(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Linkfilter(bot))