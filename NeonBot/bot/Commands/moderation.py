import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import datetime
from Commands.helper import load_data, save_data

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bannt einen User vom Server")
    @app_commands.describe(user="User der gebannt wird", reason="Grund")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Kein Grund angegeben"):
        if user == interaction.user:
            return await interaction.response.send_message("Du kannst dich nicht selbst bannen!", ephemeral=True)
        if user.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("Du kannst diesen User nicht bannen!", ephemeral=True)
        await user.ban(reason=reason)
        embed = discord.Embed(title="🔨 User gebannt", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="User",       value=f"{user.mention} (`{user.id}`)", inline=True)
        embed.add_field(name="Moderator",  value=interaction.user.mention,        inline=True)
        embed.add_field(name="Grund",      value=reason,                          inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, "BAN", user, interaction.user, reason)

    @app_commands.command(name="unban", description="Entbannt einen User")
    @app_commands.describe(user_id="User ID des gebannten Users")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        if not user_id.isdigit():
            return await interaction.response.send_message("Bitte eine gueltige User-ID eingeben!", ephemeral=True)
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            embed = discord.Embed(title="✅ User entbannt", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
            embed.add_field(name="User", value=f"{user} (`{user.id}`)")
            await interaction.response.send_message(embed=embed)
        except discord.NotFound:
            await interaction.response.send_message("User nicht gefunden!", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Dieser User ist nicht gebannt!", ephemeral=True)

    @app_commands.command(name="kick", description="Kickt einen User vom Server")
    @app_commands.describe(user="User der gekickt wird", reason="Grund")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Kein Grund angegeben"):
        if user == interaction.user:
            return await interaction.response.send_message("Du kannst dich nicht selbst kicken!", ephemeral=True)
        if user.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("Du kannst diesen User nicht kicken!", ephemeral=True)
        await user.kick(reason=reason)
        embed = discord.Embed(title="👢 User gekickt", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="User",      value=f"{user.mention} (`{user.id}`)", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention,        inline=True)
        embed.add_field(name="Grund",     value=reason,                          inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, "KICK", user, interaction.user, reason)

    @app_commands.command(name="mute", description="Mutet einen User")
    @app_commands.describe(user="User", duration="Dauer in Minuten (max 40320)", reason="Grund")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: int = 10, reason: str = "Kein Grund angegeben"):
        if user.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("Du kannst diesen User nicht muten!", ephemeral=True)
        if not 1 <= duration <= 40320:
            return await interaction.response.send_message("Dauer: 1–40320 Minuten!", ephemeral=True)
        await user.timeout(timedelta(minutes=duration), reason=reason)
        embed = discord.Embed(title="🔇 User gemutet", color=discord.Color.yellow(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="User",      value=user.mention,           inline=True)
        embed.add_field(name="Dauer",     value=f"{duration} Minuten",  inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Grund",     value=reason,                  inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, "MUTE", user, interaction.user, reason)

    @app_commands.command(name="unmute", description="Entmutet einen User")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        if not user.is_timed_out():
            return await interaction.response.send_message("Dieser User ist nicht gemutet!", ephemeral=True)
        await user.timeout(None)
        embed = discord.Embed(title="🔊 User entmutet", color=discord.Color.green())
        embed.add_field(name="User", value=user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warn", description="Verwarnt einen User")
    @app_commands.describe(user="User", reason="Grund")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Kein Grund angegeben"):
        if user.bot:
            return await interaction.response.send_message("Bots koennen nicht verwarnt werden!", ephemeral=True)
        warns = load_data("warnings.json")
        uid = str(user.id)
        if uid not in warns:
            warns[uid] = []
        warns[uid].append({"reason": reason, "mod": str(interaction.user.id), "time": datetime.datetime.utcnow().isoformat()})
        save_data("warnings.json", warns)
        embed = discord.Embed(title="⚠️ User verwarnt", color=discord.Color.yellow())
        embed.add_field(name="User",                value=user.mention,          inline=True)
        embed.add_field(name="Verwarnungen gesamt", value=str(len(warns[uid])),  inline=True)
        embed.add_field(name="Grund",               value=reason,                inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, "WARN", user, interaction.user, reason)

    @app_commands.command(name="warns", description="Zeigt Verwarnungen eines Users")
    @app_commands.default_permissions(moderate_members=True)
    async def warns(self, interaction: discord.Interaction, user: discord.Member):
        warns = load_data("warnings.json")
        user_warns = warns.get(str(user.id), [])
        embed = discord.Embed(title=f"⚠️ Verwarnungen: {user.display_name}", color=discord.Color.orange())
        if not user_warns:
            embed.description = "Keine Verwarnungen. ✅"
        else:
            for i, w in enumerate(user_warns, 1):
                embed.add_field(name=f"#{i}", value=w["reason"], inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearwarns", description="Loescht alle Verwarnungen eines Users")
    @app_commands.default_permissions(administrator=True)
    async def clearwarns(self, interaction: discord.Interaction, user: discord.Member):
        warns = load_data("warnings.json")
        warns[str(user.id)] = []
        save_data("warnings.json", warns)
        await interaction.response.send_message(f"✅ Alle Verwarnungen von {user.mention} geloescht!", ephemeral=True)

    @app_commands.command(name="clear", description="Loescht Nachrichten (max 100)")
    @app_commands.describe(amount="Anzahl Nachrichten")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int = 10):
        if not 1 <= amount <= 100:
            return await interaction.response.send_message("Bitte zwischen 1 und 100!", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ {len(deleted)} Nachrichten geloescht!", ephemeral=True)

    @app_commands.command(name="slowmode", description="Setzt Slowmode im Channel")
    @app_commands.describe(seconds="Sekunden (0 = aus)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int = 0):
        if not 0 <= seconds <= 21600:
            return await interaction.response.send_message("Zwischen 0 und 21600 Sekunden!", ephemeral=True)
        await interaction.channel.edit(slowmode_delay=seconds)
        msg = "✅ Slowmode deaktiviert!" if seconds == 0 else f"✅ Slowmode: {seconds} Sekunden"
        await interaction.response.send_message(msg)

    async def _log(self, guild, action, target, mod, reason):
        config = load_data("config.json")
        ch_id  = config.get(str(guild.id), {}).get("log_channel")
        if not ch_id: return
        channel = guild.get_channel(int(ch_id))
        if not channel: return
        colors = {"BAN": discord.Color.red(), "KICK": discord.Color.orange(),
                  "MUTE": discord.Color.yellow(), "WARN": discord.Color.gold()}
        embed = discord.Embed(title=f"📋 Mod-Log: {action}", color=colors.get(action, discord.Color.blurple()), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="User",      value=f"{target} (`{target.id}`)", inline=True)
        embed.add_field(name="Moderator", value=str(mod),                    inline=True)
        embed.add_field(name="Grund",     value=reason,                      inline=False)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
