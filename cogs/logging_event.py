import discord
from discord.ext import commands

class Loggingevent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="logging_event", description="Befehl logging_event")
    async def logging_event(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (logging_event) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Loggingevent(bot))