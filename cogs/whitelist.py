import discord
from discord.ext import commands
import datetime

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="whitelist", description="Befehl whitelist")\n    async def whitelist(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Whitelist(bot))