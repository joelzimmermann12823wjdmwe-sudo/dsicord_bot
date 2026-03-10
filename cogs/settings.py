import discord
from discord.ext import commands
import datetime

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="settings", description="Öffnet das Einstellungsmenü des Bots.")
    async def settings(self, ctx):
        await ctx.send("⚙️ Einstellungen: Bald verfügbar!")

async def setup(bot):
    await bot.add_cog(Settings(bot))