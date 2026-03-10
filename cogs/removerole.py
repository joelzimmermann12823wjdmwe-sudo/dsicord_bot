import discord
from discord.ext import commands
import datetime

class RemoveRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="removerole", description="Entfernt eine Rolle")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        await ctx.send(f"❌ Rolle {role.name} von {member.name} entfernt.")

async def setup(bot):
    await bot.add_cog(RemoveRole(bot))