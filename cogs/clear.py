import discord
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command(name="clear", aliases=["purge", "prune"])
    async def clear(self, ctx: commands.Context, amount: int = 10):
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 {len(deleted) - 1} Nachrichten gelöscht.", delete_after=5)


async def setup(bot):
    await bot.add_cog(Clear(bot))
