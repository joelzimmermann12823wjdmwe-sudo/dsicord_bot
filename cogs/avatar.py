import discord
from discord.ext import commands
import datetime
import asyncio

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar")
    async def avatar(self, ctx, m: discord.Member=None): m=m or ctx.author; await ctx.send(m.display_avatar.url)

async def setup(bot):
    await bot.add_cog(Avatar(bot))