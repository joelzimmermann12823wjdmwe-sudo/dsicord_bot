import discord
from discord.ext import commands

class Vckick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vckick", description="Befehl vckick")
    async def vckick(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (vckick) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Vckick(bot))