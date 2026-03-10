import discord
from discord.ext import commands

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nuke", description="Befehl nuke")
    async def nuke(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (nuke) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Nuke(bot))