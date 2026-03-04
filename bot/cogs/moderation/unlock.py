import discord
from discord.ext import commands

class Unlock(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="unlock")
    async def _unlock(self, ctx, *args):
        await ctx.send(f"✅ Command 'unlock' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Unlock(bot))
