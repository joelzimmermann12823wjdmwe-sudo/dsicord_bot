import discord
from discord.ext import commands
import datetime
import asyncio

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="whitelist")
    async def whitelist(self, ctx): await ctx.send("⚪ Whitelist-System ist aktiv.")

async def setup(bot):
    await bot.add_cog(Whitelist(bot))