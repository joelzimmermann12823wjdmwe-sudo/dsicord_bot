import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="kick", description="Befehl kick")
    async def kick(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (kick) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Kick(bot))