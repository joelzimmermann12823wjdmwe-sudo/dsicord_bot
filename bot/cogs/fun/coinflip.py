import random
from discord.ext import commands

class Coinflip(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="coinflip")
    async def _coinflip(self, ctx):
        await ctx.send(f"🎮 Fun: coinflip läuft!")

async def setup(bot): await bot.add_cog(Coinflip(bot))
