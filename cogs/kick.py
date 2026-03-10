import discord
from discord.ext import commands
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="kick", description="Wirft einen Nutzer vom Server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Kein Grund"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.name} gekickt.")

async def setup(bot):
    await bot.add_cog(Kick(bot))