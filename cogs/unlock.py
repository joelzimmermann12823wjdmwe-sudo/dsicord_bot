import discord
from discord.ext import commands

class Unlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unlock", description="Befehl unlock")
    async def unlock(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (unlock) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Unlock(bot))