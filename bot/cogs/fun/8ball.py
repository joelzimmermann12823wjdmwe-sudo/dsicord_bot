import random
from discord.ext import commands

class 8ball(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="8ball")
    async def _8ball(self, ctx):
        await ctx.send(f"🎮 Fun: 8ball läuft!")

async def setup(bot): await bot.add_cog(8ball(bot))
