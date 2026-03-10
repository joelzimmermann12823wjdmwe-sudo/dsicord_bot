import discord
from discord.ext import commands
import datetime
import asyncio

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Kein Grund"): await member.kick(reason=reason); await ctx.send(f"👢 {member} gekickt.")

async def setup(bot):
    await bot.add_cog(Kick(bot))