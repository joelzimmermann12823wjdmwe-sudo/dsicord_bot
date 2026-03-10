import discord
from discord.ext import commands

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="mute", description="Befehl mute")
    async def mute(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (mute) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Mute(bot))