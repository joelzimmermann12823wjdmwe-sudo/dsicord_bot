import discord
from discord.ext import commands
from datetime import datetime

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.neon_color = discord.Color.from_rgb(0, 212, 255)

    async def get_log_channel(self, guild):
        """Holt den Log-Kanal aus der Supabase Datenbank."""
        if not self.bot.db:
            return None
        
        res = self.bot.db.table("guild_settings").select("log_channel_id").eq("guild_id", str(guild.id)).execute()
        
        if res.data and res.data[0]['log_channel_id']:
            return guild.get_channel(int(res.data[0]['log_channel_id']))
        return None

    # --- EVENT: NACHRICHT GELÖSCHT ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        
        channel = await self.get_log_channel(message.guild)
        if not channel: return

        embed = discord.Embed(title="🗑️ Nachricht gelöscht", color=discord.Color.orange(), timestamp=datetime.utcnow())
        embed.add_field(name="Autor", value=f"{message.author.mention} ({message.author.id})", inline=False)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=False)
        embed.add_field(name="Inhalt", value=message.content or "*(Kein Text / Bild)*", inline=False)
        embed.set_footer(text="Neon Logging System")

        await channel.send(embed=embed)

    # --- EVENT: USER GEBANNT ---
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        channel = await self.get_log_channel(guild)
        if not channel: return

        # Wir suchen im Audit-Log nach dem Grund und dem Moderator
        moderator = "Unbekannt"
        reason = "Kein Grund angegeben"
        
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                moderator = entry.user
                reason = entry.reason
                break

        embed = discord.Embed(title="🔨 Mitglied gebannt", color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
        embed.add_field(name="Moderator", value=moderator, inline=True)
        embed.add_field(name="Grund", value=reason, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)

        await channel.send(embed=embed)

    # --- EVENT: KANAL ERSTELLT/GELÖSCHT (ANTI-NUKE VORSTUFE) ---
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = await self.get_log_channel(channel.guild)
        if not log_channel: return

        embed = discord.Embed(title="📂 Kanal gelöscht", color=self.neon_color, timestamp=datetime.utcnow())
        embed.add_field(name="Name", value=f"#{channel.name}", inline=True)
        embed.add_field(name="Typ", value=str(channel.type), inline=True)
        
        await log_channel.send(embed=embed)

    # --- EVENT: ROLLENÄNDERUNGEN ---
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        channel = await self.get_log_channel(role.guild)
        if not channel: return
        await channel.send(f"🆕 Eine neue Rolle wurde erstellt: **{role.name}**")

async def setup(bot):
    await bot.add_cog(Logging(bot))