import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="Bannt User")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, grund="Kein Grund"):
        await member.ban(reason=grund)
        await ctx.send(f"🚫 {member.name} wurde gebannt.")

async def setup(bot):
    await bot.add_cog(Ban(bot))