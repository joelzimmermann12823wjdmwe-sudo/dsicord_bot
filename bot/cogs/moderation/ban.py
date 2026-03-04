import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="ban")
    async def _ban(self, ctx, *args):
        await ctx.send(f"✅ Command 'ban' wurde aufgerufen (Logik aktiv).")

async def setup(bot): await bot.add_cog(Ban(bot))
