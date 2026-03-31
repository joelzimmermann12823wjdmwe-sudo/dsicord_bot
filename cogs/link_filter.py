import re

import discord
from discord.ext import commands


class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_regex = re.compile(r"(https?://\S+|discord\.gg/\S+)", re.IGNORECASE)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if self.bot.get_cog("AutoMod") is not None:
            return

        if message.author.guild_permissions.administrator:
            return

        if getattr(self.bot, "db", None):
            try:
                res = (
                    self.bot.db.table("guild_settings")
                    .select("automod_enabled, link_filter_enabled")
                    .eq("guild_id", str(message.guild.id))
                    .execute()
                )
                if not res.data:
                    return

                data = res.data[0]
                if not data.get("automod_enabled", True) or not data.get("link_filter_enabled"):
                    return
            except Exception:
                return

        if self.link_regex.search(message.content):
            try:
                await message.delete()
            except discord.HTTPException:
                return

            await message.channel.send(
                f"⚠️ {message.author.mention}, das Senden von Links ist hier nicht erlaubt!",
                delete_after=5,
            )


async def setup(bot):
    await bot.add_cog(LinkFilter(bot))
