import discord
from discord.ext import commands

class Nuke(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="nuke")
    async def _nuke(self, ctx, *args):
        await ctx.send(f"✅ Command 'nuke' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Nuke(bot))
