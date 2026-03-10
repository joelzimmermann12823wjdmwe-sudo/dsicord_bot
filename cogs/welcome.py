import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="welcome", description="Befehl welcome")
    async def welcome(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (welcome) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))