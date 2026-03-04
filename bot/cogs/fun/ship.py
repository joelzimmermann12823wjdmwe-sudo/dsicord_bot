import random
from discord.ext import commands

class Ship(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="ship")
    async def _ship(self, ctx):
        await ctx.send(f"🎮 Fun: ship läuft!")

async def setup(bot): await bot.add_cog(Ship(bot))
