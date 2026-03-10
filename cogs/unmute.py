import discord
from discord.ext import commands
import datetime

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unmute", description="Stummschaltung aufheben")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 Stummschaltung für **{member.mention}** aufgehoben.")

async def setup(bot):
    await bot.add_cog(Unmute(bot))