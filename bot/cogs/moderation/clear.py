import discord
from discord.ext import commands
class Clear(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount+1); await ctx.send(f"🧹 {amount} gelöscht.", delete_after=2)
async def setup(bot): await bot.add_cog(Clear(bot))
