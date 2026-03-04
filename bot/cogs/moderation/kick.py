import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="kick")
    async def _kick(self, ctx, *args):
        await ctx.send(f"✅ Command 'kick' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Kick(bot))
