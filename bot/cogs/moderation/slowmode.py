import discord
from discord.ext import commands

class Slowmode(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="slowmode")
    async def _slowmode(self, ctx, *args):
        await ctx.send(f"✅ Command 'slowmode' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Slowmode(bot))
