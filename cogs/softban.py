import discord
from discord.ext import commands

class Softban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="softban", description="Befehl softban")
    async def softban(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (softban) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Softban(bot))