import discord
from discord.ext import commands

class Vcunmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcunmute", description="Befehl vcunmute")
    async def vcunmute(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (vcunmute) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Vcunmute(bot))