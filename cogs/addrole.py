import discord
from discord.ext import commands
import datetime

class Addrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addrole", description="Weist einem Nutzer eine bestimmte Rolle zu.")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f"✅ {member.name} hat nun die Rolle {role.name}.")

async def setup(bot):
    await bot.add_cog(Addrole(bot))