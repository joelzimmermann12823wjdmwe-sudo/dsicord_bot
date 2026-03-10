import discord
from discord.ext import commands
import datetime

class VCKick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vckick", description="Kickt aus dem Voice")
    @commands.has_permissions(move_members=True)
    async def vckick(self, ctx, member: discord.Member):
        if member.voice:
            await member.move_to(None)
            await ctx.send(f"🔇 {member.name} aus dem Voice gekickt.")

async def setup(bot):
    await bot.add_cog(VCKick(bot))