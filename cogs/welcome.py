import discord
from discord.ext import commands
import datetime

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="welcome_test", description="Testet die Willkommensnachricht manuell.")
    async def welcome_test(self, ctx):
        await ctx.send("👋 Test: Willkommen auf dem Server!")

async def setup(bot):
    await bot.add_cog(Welcome(bot))