import discord
from discord.ext import commands
import datetime
import asyncio

class TestCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test")
    async def test(self, ctx): await ctx.send("🚀 Test erfolgreich!")

async def setup(bot):
    await bot.add_cog(TestCmd(bot))