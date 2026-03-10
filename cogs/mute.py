import discord
from discord.ext import commands
import datetime

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="mute", description="Stummschaltung")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minuten: int = 10):
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=minuten))
        await ctx.send(f"🔇 **{member.mention}** wurde für {minuten} Minuten stummgeschaltet.")

async def setup(bot):
    await bot.add_cog(Mute(bot))