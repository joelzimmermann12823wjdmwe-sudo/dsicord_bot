import discord
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="settings", description="Befehl settings")
    async def settings(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (settings) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Settings(bot))