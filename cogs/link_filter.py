import discord
from discord.ext import commands

class Linkfilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="link_filter", description="Befehl link_filter")
    async def link_filter(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (link_filter) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Linkfilter(bot))