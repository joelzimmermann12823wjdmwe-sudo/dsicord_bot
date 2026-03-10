import discord
from discord.ext import commands
import datetime

class Testcmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test_cmd", description="Befehl test_cmd")\n    async def test_cmd(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Testcmd(bot))