import re

import discord
from discord.ext import commands


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_regex = re.compile(r"(https?://\S+|discord\.gg/\S+)", re.IGNORECASE)

    async def get_settings(self, guild_id):
        settings = {
            "automod_enabled": True,
            "link_filter_enabled": False,
        }
        if not self.bot.db:
            return settings

        try:
            res = (
                self.bot.db.table("guild_settings")
                .select("automod_enabled, link_filter_enabled")
                .eq("guild_id", str(guild_id))
                .execute()
            )
            if res.data:
                settings.update(res.data[0])
        except Exception:
            pass

        return settings

    async def get_bad_words(self, guild_id):
        if not self.bot.db:
            return []

        try:
            res = self.bot.db.table("bad_words").select("word").eq("guild_id", str(guild_id)).execute()
            return [item["word"].lower() for item in res.data] if res.data else []
        except Exception:
            return []

    async def is_whitelisted(self, guild_id, user):
        if not self.bot.db:
            return user.guild_permissions.administrator if hasattr(user, "guild_permissions") else False

        if user.guild_permissions.administrator:
            return True

        try:
            ids_to_check = [str(user.id)] + [str(role.id) for role in user.roles]
            res = (
                self.bot.db.table("whitelist")
                .select("*")
                .eq("guild_id", str(guild_id))
                .in_("target_id", ids_to_check)
                .execute()
            )
            return bool(res.data)
        except Exception:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        settings = await self.get_settings(message.guild.id)
        if not settings.get("automod_enabled", True):
            return

        try:
            if await self.is_whitelisted(message.guild.id, message.author):
                return
        except Exception:
            pass

        content = message.content.lower()

        try:
            bad_words = await self.get_bad_words(message.guild.id)
            if bad_words and any(word in content for word in bad_words):
                await message.delete()
                await message.channel.send(
                    f"🚫 {message.author.mention}, deine Nachricht enthielt verbotene Woerter!",
                    delete_after=5,
                )
                return
        except Exception:
            pass

        try:
            if settings.get("link_filter_enabled") and self.link_regex.search(message.content):
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, Links sind hier nicht erlaubt!",
                    delete_after=5,
                )
                return
        except Exception:
            pass

        try:
            if not self.bot.db:
                return

            res = (
                self.bot.db.table("bot_only_channels")
                .select("*")
                .eq("guild_id", str(message.guild.id))
                .eq("channel_id", str(message.channel.id))
                .execute()
            )
            if res.data and not message.content.startswith(("!", "/")):
                await message.delete()
                try:
                    await message.author.send(
                        f"Im Kanal **#{message.channel.name}** sind nur Bot-Befehle erlaubt!"
                    )
                except Exception:
                    pass
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
