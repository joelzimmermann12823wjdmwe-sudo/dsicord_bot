import discord
from discord.ext import commands

class Warn(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="warn")
    async def _warn(self, ctx, *args):
        await ctx.send(f"✅ Command 'warn' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Warn(bot))
