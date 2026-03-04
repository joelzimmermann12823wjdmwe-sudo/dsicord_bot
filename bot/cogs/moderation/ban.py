import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, r="Kein Grund"):
        await member.ban(reason=r); await ctx.send(f"🚫 {member} gebannt.")
async def setup(bot): await bot.add_cog(Ban(bot))
