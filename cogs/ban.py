import discord
from discord.ext import commands
import datetime
import asyncio

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Kein Grund"): await member.ban(reason=reason); await ctx.send(f"🚫 {member} gebannt.")

async def setup(bot):
    await bot.add_cog(Ban(bot))