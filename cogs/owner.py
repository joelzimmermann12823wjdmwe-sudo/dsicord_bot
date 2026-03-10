import discord
from discord.ext import commands
import datetime
import asyncio

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx): await ctx.send("💤 Offline."); await self.bot.close()

async def setup(bot):
    await bot.add_cog(Owner(bot))