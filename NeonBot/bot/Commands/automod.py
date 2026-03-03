import discord
from discord.ext import commands
import re

class AUTOMOD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Erweitere diese Liste beliebig
        self.blacklist = ["idiot", "arsch", "huso", "bastard"] 

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignoriere Bots und Admins (optional)
        if message.author.bot or message.author.guild_permissions.manage_messages:
            return

        content = message.content.lower()

        # 1. Schimpfwort-Filter
        if any(word in content for word in self.blacklist):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bitte achte auf deine Wortwahl!", delete_after=5)
            except: pass
            return

        # 2. Invite-Link Sperre
        if "discord.gg/" in content or "discord.com/invite/" in content:
            try:
                await message.delete()
                await message.channel.send(f"🚫 {message.author.mention}, Einladungslinks sind hier nicht erlaubt!", delete_after=5)
            except: pass
            return

        # 3. Caps-Spam Schutz
        if len(message.content) > 15 and sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.7:
            try:
                await message.delete()
                await message.channel.send(f"📢 {message.author.mention}, bitte schreibe nicht nur in Großbuchstaben!", delete_after=5)
            except: pass

async def setup(bot):
    await bot.add_cog(AUTOMOD(bot))