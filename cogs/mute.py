import discord
from discord.ext import commands
import datetime
import asyncio

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, zeit: int = 10): await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=zeit)); await ctx.send(f"🔇 {member} für {zeit}m stumm.")

async def setup(bot):
    await bot.add_cog(Mute(bot))