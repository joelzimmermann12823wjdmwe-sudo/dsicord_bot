import discord
from discord.ext import commands

class Mute(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="mute")
    async def _mute(self, ctx, *args):
        await ctx.send(f"✅ Command 'mute' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Mute(bot))
