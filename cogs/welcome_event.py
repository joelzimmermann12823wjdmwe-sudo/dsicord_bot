import discord
from discord.ext import commands

class Welcomeevent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="welcome_event", description="Befehl welcome_event")
    async def welcome_event(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (welcome_event) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Welcomeevent(bot))