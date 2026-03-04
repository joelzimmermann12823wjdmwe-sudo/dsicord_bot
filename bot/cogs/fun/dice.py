import random
from discord.ext import commands

class Dice(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="dice")
    async def _dice(self, ctx):
        await ctx.send(f"🎮 Fun: dice läuft!")

async def setup(bot): await bot.add_cog(Dice(bot))
