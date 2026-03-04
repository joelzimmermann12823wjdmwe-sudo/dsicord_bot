import random
from discord.ext import commands

class Joke(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="joke")
    async def _joke(self, ctx):
        await ctx.send(f"🎮 Fun: joke läuft!")

async def setup(bot): await bot.add_cog(Joke(bot))
