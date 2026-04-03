import discord
from discord.ext import commands

class TestCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_developer(self):
        async def predicate(ctx):
            return ctx.author.id in self.bot.permissions.get("developers", [])
        return commands.check(predicate)

    @commands.hybrid_command(name="test_cmd", description="Internes Testmodul für Entwickler.")
    @is_developer()
    async def test_cmd(self, ctx):
        await ctx.send("🛠️ Test erfolgreich! Die Cogs-Architektur funktioniert wunderbar")

async def setup(bot):
    await bot.add_cog(TestCmd(bot))
