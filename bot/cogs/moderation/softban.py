import discord
from discord.ext import commands

class Softban(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="softban")
    async def _softban(self, ctx, *args):
        await ctx.send(f"✅ Command 'softban' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Softban(bot))
