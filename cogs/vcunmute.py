import discord
from discord.ext import commands
import datetime

class Vcunmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcunmute", description="Befehl vcunmute")\n    async def vcunmute(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Vcunmute(bot))