import random
from discord.ext import commands

class Dog(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="dog")
    async def _dog(self, ctx):
        await ctx.send(f"🎮 Fun: dog läuft!")

async def setup(bot): await bot.add_cog(Dog(bot))
