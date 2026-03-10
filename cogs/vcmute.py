import discord
from discord.ext import commands
import datetime

class Vcmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcmute", description="Befehl vcmute")\n    async def vcmute(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Vcmute(bot))