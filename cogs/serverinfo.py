import discord
from discord.ext import commands
import datetime
import asyncio

class Serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo")
    async def serverinfo(self, ctx): g=ctx.guild; e=discord.Embed(title=g.name); e.add_field(name="Member", value=g.member_count); await ctx.send(embed=e)

async def setup(bot):
    await bot.add_cog(Serverinfo(bot))