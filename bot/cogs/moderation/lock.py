import discord
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="lock")
    async def _lock(self, ctx, *args):
        await ctx.send(f"✅ Command 'lock' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Lock(bot))
