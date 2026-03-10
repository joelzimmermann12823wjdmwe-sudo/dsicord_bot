import discord
from discord.ext import commands
import datetime

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return
        if "discord.gg/" in msg.content.lower():
            await msg.delete()
            await msg.channel.send("🚫 Keine Werbung!", delete_after=3)

async def setup(bot):
    await bot.add_cog(Automod(bot))