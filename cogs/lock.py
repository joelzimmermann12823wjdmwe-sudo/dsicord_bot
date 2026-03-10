import discord
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="lock", description="Befehl lock")
    async def lock(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (lock) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Lock(bot))