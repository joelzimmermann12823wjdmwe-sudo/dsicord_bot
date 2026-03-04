import random
from discord.ext import commands

class Slap(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="slap")
    async def _slap(self, ctx):
        await ctx.send(f"🎮 Fun: slap läuft!")

async def setup(bot): await bot.add_cog(Slap(bot))
