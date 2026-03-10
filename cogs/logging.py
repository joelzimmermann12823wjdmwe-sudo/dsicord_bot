import discord
from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="logging", description="Befehl logging")
    async def logging(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (logging) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Logging(bot))