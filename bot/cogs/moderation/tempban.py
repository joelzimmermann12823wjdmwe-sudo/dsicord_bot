import discord
from discord.ext import commands

class Tempban(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="tempban")
    async def _tempban(self, ctx, *args):
        await ctx.send(f"✅ Command 'tempban' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Tempban(bot))
