import discord
from discord.ext import commands
import datetime
import collections

class AntiNuke(commands.Cog):
    DEFAULT_LIMIT = 5
    WINDOW_SECONDS = 3

    def __init__(self, bot):
        self.bot = bot
        self.message_spam_tracker = collections.defaultdict(list)
        self.channel_delete_tracker = collections.defaultdict(list)
        self.channel_create_tracker = collections.defaultdict(list)
        self.role_delete_tracker = collections.defaultdict(list)
        self.role_create_tracker = collections.defaultdict(list)

    async def is_whitelisted(self, guild_id, target_id):
        if not getattr(self.bot, "db", None):
            return False

        res = self.bot.db.table("whitelist").select("*").eq("guild_id", str(guild_id)).eq("target_id", str(target_id)).execute()
        return len(res.data) > 0

    async def get_log_channel(self, guild):
        if not getattr(self.bot, "db", None):
            return None

        res = self.bot.db.table("guild_settings").select("log_channel_id").eq("guild_id", str(guild.id)).execute()
        if res.data and res.data[0].get("log_channel_id"):
            return guild.get_channel(int(res.data[0]["log_channel_id"]))
        return None

    async def get_limit(self, guild_id):
        if not getattr(self.bot, "db", None):
            return self.DEFAULT_LIMIT

        try:
            res = self.bot.db.table("guild_settings").select("antinuke_limit").eq("guild_id", str(guild_id)).execute()
            if res.data and res.data[0].get("antinuke_limit") is not None:
                limit = int(res.data[0]["antinuke_limit"])
                return max(limit, 1)
        except Exception:
            pass

        return self.DEFAULT_LIMIT

    async def clear_user_trackers(self, user_id):
        self.message_spam_tracker.pop(user_id, None)
        self.channel_delete_tracker.pop(user_id, None)
        self.channel_create_tracker.pop(user_id, None)
        self.role_delete_tracker.pop(user_id, None)
        self.role_create_tracker.pop(user_id, None)

    async def punish_nuke(self, guild, user, reason):
        try:
            await guild.ban(user, reason=f"NEON ANTI-NUKE: {reason}")
        except Exception:
            pass

        embed = discord.Embed(
            title="🚨 NUKE-ALARM VERHINDERT",
            description=f"Der User **{user}** hat versucht den Server zu nuken. ({reason})",
            color=discord.Color.red(),
        )
        embed.add_field(name="Maßnahme", value="User wurde gebannt.", inline=False)
        embed.set_footer(text="Anti-Nuke System")

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
                await log_channel.send(f"⚠️ {owner.mention if owner else 'Server-Owner'} **NUKE VERSUCH GESTOPPT!** User {user.mention} wurde gebannt.")
            except Exception:
                pass

        await self.clear_user_trackers(user.id)

    async def _track_action(self, tracker, user, guild, reason):
        now = datetime.datetime.utcnow()
        events = [t for t in tracker[user.id] if (now - t).total_seconds() < self.WINDOW_SECONDS]
        events.append(now)
        tracker[user.id] = events

        if len(events) > await self.get_limit(guild.id):
            await self.punish_nuke(guild, user, reason)
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if await self.is_whitelisted(message.guild.id, message.author.id):
            return

        if await self._track_action(self.message_spam_tracker, message.author, message.guild, "5 Nachrichten in 3 Sekunden gesendet"):
            try:
                await message.delete()
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            user = entry.user
            if not user or user.id == self.bot.user.id:
                return

            if await self.is_whitelisted(guild.id, user.id):
                return

            await self._track_action(self.channel_delete_tracker, user, guild, "5 Kanäle in 3 Sekunden gelöscht")
            return

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            user = entry.user
            if not user or user.id == self.bot.user.id:
                return

            if await self.is_whitelisted(guild.id, user.id):
                return

            await self._track_action(self.channel_create_tracker, user, guild, "5 Kanäle in 3 Sekunden erstellt")
            return

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            user = entry.user
            if not user or user.id == self.bot.user.id:
                return

            if await self.is_whitelisted(guild.id, user.id):
                return

            await self._track_action(self.role_delete_tracker, user, guild, "5 Rollen in 3 Sekunden gelöscht")
            return

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        guild = role.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            user = entry.user
            if not user or user.id == self.bot.user.id:
                return

            if await self.is_whitelisted(guild.id, user.id):
                return

            await self._track_action(self.role_create_tracker, user, guild, "5 Rollen in 3 Sekunden erstellt")
            return

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))