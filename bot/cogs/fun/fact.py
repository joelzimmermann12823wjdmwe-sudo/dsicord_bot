import random
from discord.ext import commands

class Fact(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="fact")
    async def _fact(self, ctx):
        await ctx.send(f"🎮 Fun: fact läuft!")

async def setup(bot): await bot.add_cog(Fact(bot))
