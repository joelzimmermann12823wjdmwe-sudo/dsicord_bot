import discord
from discord.ext import commands
import datetime

class Softban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="softban", description="Befehl softban")\n    async def softban(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")

async def setup(bot):
    await bot.add_cog(Softban(bot))