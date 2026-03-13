import discord
from discord.ext import commands
import re

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_regex = re.compile(r"(https?://\S+)")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return
        
        # Einfacher Filter: Löscht Nachrichten mit Links (Logik kann mit DB erweitert werden)
        if self.link_regex.search(message.content):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, das Senden von Links ist hier nicht erlaubt!", delete_after=5)

async def setup(bot):
    await bot.add_cog(LinkFilter(bot))
