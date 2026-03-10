import discord
from discord.ext import commands

class Serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo", description="Befehl serverinfo")
    async def serverinfo(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (serverinfo) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Serverinfo(bot))