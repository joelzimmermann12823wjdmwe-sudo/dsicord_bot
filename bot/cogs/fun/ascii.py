import random
from discord.ext import commands

class Ascii(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="ascii")
    async def _ascii(self, ctx):
        await ctx.send(f"🎮 Fun: ascii läuft!")

async def setup(bot): await bot.add_cog(Ascii(bot))
