import collections
import datetime

import discord
from discord.ext import commands


class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = collections.defaultdict(list)

    async def is_whitelisted(self, guild_id, target_id):
        if not self.bot.db:
            return False

        try:
            res = (
                self.bot.db.table("whitelist")
                .select("*")
                .eq("guild_id", str(guild_id))
                .eq("target_id", str(target_id))
                .execute()
            )
            return bool(res.data)
        except Exception:
            return False

    async def get_limit(self, guild_id):
        default_limit = 10
        if not self.bot.db:
            return default_limit

        try:
            res = (
                self.bot.db.table("guild_settings")
                .select("antinuke_limit")
                .eq("guild_id", str(guild_id))
                .execute()
            )
            if res.data and res.data[0].get("antinuke_limit"):
                return max(int(res.data[0]["antinuke_limit"]), 1)
        except Exception:
            pass

        return default_limit

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild

        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                user = entry.user
                if user is None or self.bot.user is None or user.id == self.bot.user.id:
                    return

                if await self.is_whitelisted(guild.id, user.id):
                    return

                limit = await self.get_limit(guild.id)
                key = (guild.id, user.id)
                now = datetime.datetime.utcnow()

                self.tracker[key] = [
                    timestamp
                    for timestamp in self.tracker[key]
                    if (now - timestamp).total_seconds() < 60
                ]
                self.tracker[key].append(now)

                if len(self.tracker[key]) > limit:
                    self.tracker.pop(key, None)
                    await self.punish_nuke(guild, user, "Massenloeschung von Kanaelen")
                return
        except (discord.Forbidden, discord.HTTPException):
            return

    async def punish_nuke(self, guild, user, reason):
        try:
            await guild.ban(user, reason=f"NEON ANTI-NUKE: {reason}")
        except Exception:
            pass

        embed = discord.Embed(
            title="🚨 Nuke-Alarm verhindert",
            description=f"Der User **{user}** hat versucht, den Server zu nuken (**{reason}**).",
            color=discord.Color.red(),
        )
        embed.add_field(name="Aktion", value="User wurde permanent gebannt.")

        if guild.owner:
            try:
                await guild.owner.send(embed=embed)
            except Exception:
                pass

        if not self.bot.db:
            return

        try:
            res = (
                self.bot.db.table("guild_settings")
                .select("log_channel_id")
                .eq("guild_id", str(guild.id))
                .execute()
            )
            log_channel_id = res.data[0].get("log_channel_id") if res.data else None
            if not log_channel_id:
                return

            log_channel = guild.get_channel(int(log_channel_id))
            if log_channel is None:
                return

            owner_mention = guild.owner.mention if guild.owner else "@owner"
            await log_channel.send(
                f"⚠️ {owner_mention} **NUKE-VERSUCH GESTOPPT!** User {user.mention} wurde entfernt."
            )
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
