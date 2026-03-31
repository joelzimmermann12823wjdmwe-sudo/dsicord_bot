import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="kick")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} wurde gekickt. Grund: {reason or 'kein Grund angegeben'}.")


def setup(bot):
    bot.add_cog(Kick(bot))
