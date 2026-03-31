import discord
from discord.ext import commands
import re

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_regex = re.compile(r"(https?://\S+|www\.\S+|discord\.(?:gg|com/invite)/\S+|invite\.gg/\S+)", re.IGNORECASE)
        self.invite_regex = re.compile(r"(discord\.gg/|discord(?:app)?\.com/invite/|invite\.gg/)", re.IGNORECASE)

    async def get_bad_words(self, guild_id):
        """Lädt die Schimpfwörter für diesen Server aus Supabase."""
        if not getattr(self.bot, "db", None):
            return []

        res = self.bot.db.table("bad_words").select("word").eq("guild_id", str(guild_id)).execute()
        return [item["word"].lower() for item in res.data]

    async def is_whitelisted(self, guild_id, user):
        """Prüft Whitelist für User und deren Rollen."""
        if user.guild_permissions.administrator:
            return True

        if not getattr(self.bot, "db", None):
            return False

        ids_to_check = [str(user.id)] + [str(role.id) for role in user.roles]
        res = self.bot.db.table("whitelist").select("*").eq("guild_id", str(guild_id)).in_("target_id", ids_to_check).execute()
        return len(res.data) > 0

    async def get_log_channel(self, guild):
        if not getattr(self.bot, "db", None):
            return None

        res = self.bot.db.table("guild_settings").select("log_channel_id").eq("guild_id", str(guild.id)).execute()
        if res.data and res.data[0].get("log_channel_id"):
            return guild.get_channel(int(res.data[0]["log_channel_id"]))
        return None

    def _truncate(self, text, limit=800):
        if not text:
            return "(keine Nachricht)"
        return text if len(text) <= limit else text[:limit - 3] + "..."

    async def notify_owner(self, guild, offender, reason, channel, content):
        embed = discord.Embed(
            title="🚨 AutoMod Alarm",
            description=f"Der User **{offender}** wurde von der AutoMod geprüft.",
            color=discord.Color.red(),
        )
        embed.add_field(name="Grund", value=reason, inline=False)
        embed.add_field(name="Kanal", value=channel.mention if channel else "Unbekannt", inline=False)
        embed.add_field(name="Nachricht", value=self._truncate(content), inline=False)
        embed.set_footer(text="AutoMod System")

        owner = guild.owner
        if owner is None and guild.owner_id:
            try:
                owner = await guild.fetch_member(guild.owner_id)
            except Exception:
                owner = None

        if owner:
            try:
                await owner.send(embed=embed)
            except Exception:
                pass

        log_channel = await self.get_log_channel(guild)
        if log_channel:
            try:
                await log_channel.send(embed=embed)
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if await self.is_whitelisted(message.guild.id, message.author):
            return

        content = message.content.lower() if message.content else ""

        bad_words = await self.get_bad_words(message.guild.id)
        if bad_words and any(word in content for word in bad_words):
            try:
                await message.delete()
            except discord.HTTPException:
                pass

            await message.channel.send(
                f"🚫 {message.author.mention}, deine Nachricht enthielt verbotene Wörter!",
                delete_after=5,
            )
            await self.notify_owner(message.guild, message.author, "Verbotenes Wort gefunden", message.channel, message.content)
            return

        res = None
        if getattr(self.bot, "db", None):
            try:
                res = self.bot.db.table("guild_settings").select("link_filter_enabled").eq("guild_id", str(message.guild.id)).execute()
            except Exception:
                res = None

        if res and res.data and res.data[0].get("link_filter_enabled"):
            if self.url_regex.search(content) or self.invite_regex.search(content):
                try:
                    await message.delete()
                except discord.HTTPException:
                    pass

                await message.channel.send(
                    f"⚠️ {message.author.mention}, Links und Einladungen sind hier nicht erlaubt!",
                    delete_after=5,
                )
                await self.notify_owner(message.guild, message.author, "Link- oder Einladungs-Filter ausgelöst", message.channel, message.content)
                return

        if getattr(self.bot, "db", None):
            try:
                res_chan = self.bot.db.table("bot_only_channels").select("*").eq("guild_id", str(message.guild.id)).eq("channel_id", str(message.channel.id)).execute()
            except Exception:
                res_chan = None

            if res_chan and res_chan.data:
                if not message.content.startswith(("!", "/")):
                    try:
                        await message.delete()
                    except discord.HTTPException:
                        pass
                    await message.author.send(f"Im Kanal **#{message.channel.name}** sind nur Bot-Befehle erlaubt!")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))