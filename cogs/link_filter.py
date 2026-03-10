import discord
from discord.ext import commands
import datetime

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return
        if "http" in msg.content and not msg.author.guild_permissions.administrator:
            await msg.delete()
            await msg.channel.send("🔗 Links sind verboten!", delete_after=3)

async def setup(bot):
    await bot.add_cog(LinkFilter(bot))