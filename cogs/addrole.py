import discord
from discord.ext import commands
import datetime
import asyncio

class Addrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addrole")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role): await member.add_roles(role); await ctx.send(f"✅ Rolle {role.name} hinzugefügt.")

async def setup(bot):
    await bot.add_cog(Addrole(bot))