import discord
from discord.ext import commands
import datetime
import asyncio

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping")
    async def ping(self, ctx): await ctx.send(f"🏓 {round(self.bot.latency*1000)}ms")

async def setup(bot):
    await bot.add_cog(Ping(bot))