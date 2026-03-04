import random
from discord.ext import commands

class Hug(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="hug")
    async def _hug(self, ctx):
        await ctx.send(f"🎮 Fun: hug läuft!")

async def setup(bot): await bot.add_cog(Hug(bot))
