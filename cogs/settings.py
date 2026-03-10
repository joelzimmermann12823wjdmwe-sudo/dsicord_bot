import discord
from discord.ext import commands
import datetime
import asyncio

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="settings")
    async def settings(self, ctx): await ctx.send("⚙️ Bot-Einstellungen (In Arbeit)")

async def setup(bot):
    await bot.add_cog(Settings(bot))