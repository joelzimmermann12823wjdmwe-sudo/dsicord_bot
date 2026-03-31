import discord
from discord.ext import commands

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(moderate_members=True)
    @commands.hybrid_command(name="timeout")
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: int, *, reason: str = None):
        await member.timeout_for(duration * 60, reason=reason)
        await ctx.send(f"✅ {member.mention} wurde für {duration} Minuten in Timeout geschickt.")


async def setup(bot):
    await bot.add_cog(Timeout(bot))
