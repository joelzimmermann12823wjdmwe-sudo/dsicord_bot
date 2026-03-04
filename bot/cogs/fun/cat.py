import random
from discord.ext import commands

class Cat(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="cat")
    async def _cat(self, ctx):
        await ctx.send(f"🎮 Fun: cat läuft!")

async def setup(bot): await bot.add_cog(Cat(bot))
