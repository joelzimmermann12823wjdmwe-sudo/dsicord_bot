import discord
from discord.ext import commands
import datetime

class Userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo", description="Befehl userinfo")\n    async def userinfo(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Userinfo(bot))