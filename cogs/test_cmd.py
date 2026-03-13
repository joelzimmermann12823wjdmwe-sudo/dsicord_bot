import discord
from discord.ext import commands

class TestCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test_cmd", description="Internes Testmodul für Entwickler.")
    @commands.has_permissions(administrator=True)
    async def test_cmd(self, ctx):
        await ctx.send("🛠️ Test erfolgreich! Die Cogs-Architektur funktioniert einwandfrei.")

async def setup(bot):
    await bot.add_cog(TestCmd(bot))
