import discord
from discord.ext import commands
import datetime

class TestCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test", description="Ein einfacher Test-Befehl zur Funktionsprüfung.")
    async def test(self, ctx):
        await ctx.send("🚀 Alles funktioniert super!")

async def setup(bot):
    await bot.add_cog(TestCmd(bot))