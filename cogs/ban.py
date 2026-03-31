import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.hybrid_command(name="ban")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} wurde gebannt. Grund: {reason or 'kein Grund angegeben'}.")


async def setup(bot):
    await bot.add_cog(Ban(bot))
