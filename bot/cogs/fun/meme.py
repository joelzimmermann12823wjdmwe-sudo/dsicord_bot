import random
from discord.ext import commands

class Meme(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="meme")
    async def _meme(self, ctx):
        await ctx.send(f"🎮 Fun: meme läuft!")

async def setup(bot): await bot.add_cog(Meme(bot))
