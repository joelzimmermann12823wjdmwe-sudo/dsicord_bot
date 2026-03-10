import discord
from discord.ext import commands
import datetime

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="Sperrt einen Nutzer")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, grund="Kein Grund"):
        await member.ban(reason=grund)
        await ctx.send(f"🚫 **{member.name}** wurde gesperrt. | Grund: {grund}")

async def setup(bot):
    await bot.add_cog(Ban(bot))