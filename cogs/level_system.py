import discord
from discord.ext import commands

class Levelsystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="level_system", description="Befehl level_system")
    async def level_system(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (level_system) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Levelsystem(bot))