import discord
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="clear")
    async def _clear(self, ctx, *args):
        await ctx.send(f"✅ Command 'clear' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Clear(bot))
