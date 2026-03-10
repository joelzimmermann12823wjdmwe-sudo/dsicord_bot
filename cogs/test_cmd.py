import discord
from discord.ext import commands

class Testcmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test_cmd", description="Befehl test_cmd")
    async def test_cmd(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (test_cmd) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Testcmd(bot))