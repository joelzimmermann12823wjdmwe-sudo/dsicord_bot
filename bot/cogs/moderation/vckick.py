import discord
from discord.ext import commands

class Vckick(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="vckick")
    async def _vckick(self, ctx, *args):
        await ctx.send(f"✅ Command 'vckick' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Vckick(bot))
