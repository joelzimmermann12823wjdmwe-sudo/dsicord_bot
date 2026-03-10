import discord
from discord.ext import commands

class Vcmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcmute", description="Befehl vcmute")
    async def vcmute(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (vcmute) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Vcmute(bot))