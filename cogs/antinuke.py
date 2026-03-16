import discord
from discord.ext import commands
import datetime
import collections

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Lokaler Cache für schnellen Vergleich (User_ID: [Timestamps])
        self.tracker = collections.defaultdict(list)

    async def is_whitelisted(self, guild_id, target_id):
        """Prüft, ob ein User in der Supabase-Whitelist steht."""
        if not self.bot.db: return False
        res = self.bot.db.table("whitelist").select("*").eq("guild_id", str(guild_id)).eq("target_id", str(target_id)).execute()
        return len(res.data) > 0

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            user = entry.user
            if user.id == self.bot.user.id: return
            
            # Whitelist Check
            if await self.is_whitelisted(guild.id, user.id): return

            # Nuke Logik: Max 5 Kanäle in 60 Sekunden
            now = datetime.datetime.now()
            self.tracker[user.id] = [t for t in self.tracker[user.id] if (now - t).total_seconds() < 60]
            self.tracker[user.id].append(now)

            if len(self.tracker[user.id]) > 5:
                await self.punish_nuke(guild, user, "Massenlöschung von Kanälen")

    async def punish_nuke(self, guild, user, reason):
        """Bestraft den User, pingt das Team und den Owner."""
        # 1. Bann
        try: await guild.ban(user, reason=f"NEON ANTI-NUKE: {reason}")
        except: pass

        # 2. Nachricht an den Server-Owner
        embed = discord.Embed(
            title="🚨 NUKE-ALARM VERHINDERT",
            description=f"Der User **{user}** hat versucht den Server zu nuken (**{reason}**).",
            color=discord.Color.red()
        )
        embed.add_field(name="Aktion", value="User wurde permanent gebannt.")
        
        try: await guild.owner.send(embed=embed)
        except: pass

        # 3. Team-Ping im Log-Kanal
        res = self.bot.db.table("guild_settings").select("log_channel_id").eq("guild_id", str(guild.id)).execute()
        if res.data and res.data[0]['log_channel_id']:
            channel = guild.get_channel(int(res.data[0]['log_channel_id']))
            if channel:
                await channel.send(f"⚠️ {guild.owner.mention} **NUKE VERSUCH GESTOPPT!** User {user.mention} wurde entfernt.")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))