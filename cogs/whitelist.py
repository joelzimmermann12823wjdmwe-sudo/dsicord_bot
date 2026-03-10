import discord
from discord.ext import commands

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="whitelist", description="Befehl whitelist")
    async def whitelist(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (whitelist) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Whitelist(bot))