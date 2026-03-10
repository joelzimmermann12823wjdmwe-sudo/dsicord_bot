import discord
from discord.ext import commands
import datetime
import asyncio

class Userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo")
    async def userinfo(self, ctx, m: discord.Member=None): m=m or ctx.author; e=discord.Embed(title=m.name, color=m.color); e.add_field(name="ID", value=m.id); await ctx.send(embed=e)

async def setup(bot):
    await bot.add_cog(Userinfo(bot))