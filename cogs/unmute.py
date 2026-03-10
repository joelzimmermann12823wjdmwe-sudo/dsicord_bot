import discord
from discord.ext import commands

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unmute", description="Befehl unmute")
    async def unmute(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (unmute) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Unmute(bot))