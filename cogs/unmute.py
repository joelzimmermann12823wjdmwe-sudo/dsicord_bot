import discord
from discord.ext import commands
import datetime
import asyncio

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member): await member.timeout(None); await ctx.send(f"🔊 {member} entmutet.")

async def setup(bot):
    await bot.add_cog(Unmute(bot))