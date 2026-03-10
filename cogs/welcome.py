import discord
from discord.ext import commands
import datetime
import asyncio

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="welcome_test")
    async def welcome_test(self, ctx): await ctx.send("👋 Willkommens-System bereit.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))