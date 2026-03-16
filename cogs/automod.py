import discord
from discord.ext import commands
import re

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_bad_words(self, guild_id):
        """Lädt die Schimpfwörter für diesen Server aus Supabase."""
        res = self.bot.db.table("bad_words").select("word").eq("guild_id", str(guild_id)).execute()
        return [item['word'].lower() for item in res.data]

    async def is_whitelisted(self, guild_id, user):
        """Prüft Whitelist für User und deren Rollen."""
        # Admin-Check
        if user.guild_permissions.administrator: return True
        
        # Datenbank Check
        ids_to_check = [str(user.id)] + [str(role.id) for role in user.roles]
        res = self.bot.db.table("whitelist").select("*").eq("guild_id", str(guild_id)).in_("target_id", ids_to_check).execute()
        return len(res.data) > 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        
        # Falls der User whitelisted ist, ignorieren wir alles
        if await self.is_whitelisted(message.guild.id, message.author): return

        content = message.content.lower()

        # 1. SCHIMPFOWORT-FILTER
        bad_words = await self.get_bad_words(message.guild.id)
        if any(word in content for word in bad_words):
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention}, deine Nachricht enthielt verbotene Wörter!", delete_after=5)
            return

        # 2. LINK-FILTER (Falls in Settings aktiviert)
        res = self.bot.db.table("guild_settings").select("link_filter_enabled").eq("guild_id", str(message.guild.id)).execute()
        if res.data and res.data[0]['link_filter_enabled']:
            if "http://" in content or "https://" in content or "discord.gg/" in content:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, Links sind hier nicht erlaubt!", delete_after=5)
                return

        # 3. BOT-COMMANDS-ONLY CHECK
        res_chan = self.bot.db.table("bot_only_channels").select("*").eq("guild_id", str(message.guild.id)).eq("channel_id", str(message.channel.id)).execute()
        if res_chan.data:
            if not message.content.startswith(("!", "/")):
                await message.delete()
                await message.author.send(f"Im Kanal **#{message.channel.name}** sind nur Bot-Befehle erlaubt!")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))