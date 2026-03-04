import random
from discord.ext import commands

class Kill(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="kill")
    async def _kill(self, ctx):
        await ctx.send(f"🎮 Fun: kill läuft!")

async def setup(bot): await bot.add_cog(Kill(bot))
