import discord
from discord.ext import commands
import datetime

class Levelsystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="level_system", description="Befehl level_system")\n    async def level_system(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Levelsystem(bot))