import discord
from discord.ext import commands

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slowmode", description="Befehl slowmode")
    async def slowmode(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (slowmode) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Slowmode(bot))