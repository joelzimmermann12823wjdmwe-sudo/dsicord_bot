import discord
from discord.ext import commands
import datetime

class AddRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addrole", description="Gibt eine Rolle")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f"✅ Rolle {role.mention} an {member.mention} vergeben.")

async def setup(bot):
    await bot.add_cog(AddRole(bot))