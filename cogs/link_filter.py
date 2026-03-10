import discord
from discord.ext import commands
import datetime
import asyncio

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if "http" in msg.content and not msg.author.guild_permissions.administrator: await msg.delete(); await msg.channel.send("🔗 Links verboten!", delete_after=2)

async def setup(bot):
    await bot.add_cog(LinkFilter(bot))