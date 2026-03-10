import discord
from discord.ext import commands

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="automod", description="Befehl automod")
    async def automod(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (automod) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Automod(bot))