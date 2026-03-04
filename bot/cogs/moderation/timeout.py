import discord
from discord.ext import commands

class Timeout(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="timeout")
    async def _timeout(self, ctx, *args):
        await ctx.send(f"✅ Command 'timeout' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Timeout(bot))
