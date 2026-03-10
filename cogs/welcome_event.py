import discord
from discord.ext import commands
import datetime
import asyncio

class WelcomeEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, m): ch=discord.utils.get(m.guild.channels, name="welcome");
    if ch: await ch.send(f"👋 Willkommen {m.mention}!")

async def setup(bot):
    await bot.add_cog(WelcomeEvent(bot))