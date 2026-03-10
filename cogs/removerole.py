import discord
from discord.ext import commands

class Removerole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="removerole", description="Befehl removerole")
    async def removerole(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (removerole) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Removerole(bot))