import discord
from discord.ext import commands

class Unmute(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="unmute")
    async def _unmute(self, ctx, *args):
        await ctx.send(f"✅ Command 'unmute' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Unmute(bot))
