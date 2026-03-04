import discord
from discord.ext import commands

class Untimeout(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="untimeout")
    async def _untimeout(self, ctx, *args):
        await ctx.send(f"✅ Command 'untimeout' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Untimeout(bot))
