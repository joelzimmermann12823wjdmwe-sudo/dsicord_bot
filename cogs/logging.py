import discord
from discord.ext import commands
import datetime

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, m):
        ch = discord.utils.get(m.guild.channels, name="logs")
        if ch:
            await ch.send(f"🗑️ Gelöscht in {m.channel.mention}: {m.content} von {m.author}")

async def setup(bot):
    await bot.add_cog(Logging(bot))