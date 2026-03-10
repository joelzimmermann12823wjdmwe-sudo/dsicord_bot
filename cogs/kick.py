import discord
from discord.ext import commands
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="kick", description="Kickt einen Nutzer")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, grund="Kein Grund"):
        await member.kick(reason=grund)
        await ctx.send(f"👢 **{member.name}** wurde gekickt. | Grund: {grund}")

async def setup(bot):
    await bot.add_cog(Kick(bot))