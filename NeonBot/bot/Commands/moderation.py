import discord, datetime
from datetime import timedelta
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data, get_log_channel_id


class Moderation(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def _log(self, guild, action, target, mod, reason):
        ch_id = get_log_channel_id(guild.id)
        if not ch_id: return
        ch = guild.get_channel(int(ch_id))
        if not ch: return
        colors = {"BAN":discord.Color.red(),"KICK":discord.Color.orange(),"MUTE":discord.Color.yellow(),"WARN":discord.Color.gold(),"UNBAN":discord.Color.green(),"UNMUTE":discord.Color.green()}
        e = discord.Embed(title=f"📋 Mod-Log: {action}", color=colors.get(action, discord.Color.blurple()), timestamp=datetime.datetime.utcnow())
        e.add_field(name="User",      value=f"{target} (`{getattr(target,'id',target)}`)", inline=True)
        e.add_field(name="Moderator", value=str(mod),  inline=True)
        e.add_field(name="Grund",     value=reason,    inline=False)
        try: await ch.send(embed=e)
        except: pass

    @app_commands.command(name="ban", description="Bannt einen User permanent vom Server")
    @app_commands.describe(user="User", grund="Grund")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, grund: str = "Kein Grund"):
        if user == interaction.user:
            return await interaction.response.send_message("❌ Nicht dich selbst!", ephemeral=True)
        if user.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        try: await user.ban(reason=grund)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Bot hat keine Ban-Berechtigung!", ephemeral=True)
        e = discord.Embed(title="🔨 User gebannt", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        e.set_thumbnail(url=user.display_avatar.url)
        e.add_field(name="User",value=f"{user.mention} (`{user.id}`)",inline=True)
        e.add_field(name="Moderator",value=interaction.user.mention,inline=True)
        e.add_field(name="Grund",value=grund,inline=False)
        await interaction.response.send_message(embed=e)
        await self._log(interaction.guild,"BAN",user,interaction.user,grund)

    @app_commands.command(name="unban", description="Entbannt einen User per User-ID")
    @app_commands.describe(user_id="Die User-ID")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        if not user_id.strip().isdigit():
            return await interaction.response.send_message("❌ Ungueltige User-ID!", ephemeral=True)
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            e = discord.Embed(title="✅ User entbannt", color=discord.Color.green())
            e.add_field(name="User", value=f"{user} (`{user.id}`)")
            await interaction.response.send_message(embed=e)
            await self._log(interaction.guild,"UNBAN",user,interaction.user,"Entbannt")
        except discord.NotFound:
            await interaction.response.send_message("❌ User nicht gefunden!", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ User ist nicht gebannt!", ephemeral=True)

    @app_commands.command(name="kick", description="Kickt einen User vom Server")
    @app_commands.describe(user="User", grund="Grund")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, grund: str = "Kein Grund"):
        if user == interaction.user:
            return await interaction.response.send_message("❌ Nicht dich selbst!", ephemeral=True)
        if user.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        try: await user.kick(reason=grund)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Bot hat keine Kick-Berechtigung!", ephemeral=True)
        e = discord.Embed(title="👢 User gekickt", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
        e.set_thumbnail(url=user.display_avatar.url)
        e.add_field(name="User",value=f"{user.mention} (`{user.id}`)",inline=True)
        e.add_field(name="Moderator",value=interaction.user.mention,inline=True)
        e.add_field(name="Grund",value=grund,inline=False)
        await interaction.response.send_message(embed=e)
        await self._log(interaction.guild,"KICK",user,interaction.user,grund)

    @app_commands.command(name="mute", description="Mutet einen User (Discord Timeout)")
    @app_commands.describe(user="User", dauer="Minuten (max 40320)", grund="Grund")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, dauer: int = 10, grund: str = "Kein Grund"):
        if user.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        if not 1 <= dauer <= 40320:
            return await interaction.response.send_message("❌ 1–40320 Minuten!", ephemeral=True)
        try: await user.timeout(timedelta(minutes=dauer), reason=grund)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Bot hat keine Mute-Berechtigung!", ephemeral=True)
        e = discord.Embed(title="🔇 User gemutet", color=discord.Color.yellow(), timestamp=datetime.datetime.utcnow())
        e.set_thumbnail(url=user.display_avatar.url)
        e.add_field(name="User",value=user.mention,inline=True)
        e.add_field(name="Dauer",value=f"{dauer} Min",inline=True)
        e.add_field(name="Moderator",value=interaction.user.mention,inline=True)
        e.add_field(name="Grund",value=grund,inline=False)
        await interaction.response.send_message(embed=e)
        await self._log(interaction.guild,"MUTE",user,interaction.user,f"{grund} ({dauer} Min)")

    @app_commands.command(name="unmute", description="Hebt den Mute eines Users auf")
    @app_commands.describe(user="User")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        if not user.is_timed_out():
            return await interaction.response.send_message("❌ User ist nicht gemutet!", ephemeral=True)
        try: await user.timeout(None)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        e = discord.Embed(title="🔊 User entmutet", color=discord.Color.green())
        e.add_field(name="User", value=user.mention)
        await interaction.response.send_message(embed=e)
        await self._log(interaction.guild,"UNMUTE",user,interaction.user,"Mute aufgehoben")

    @app_commands.command(name="warn", description="Verwarnt einen User offiziell")
    @app_commands.describe(user="User", grund="Grund")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, grund: str = "Kein Grund"):
        if user.bot:
            return await interaction.response.send_message("❌ Bots koennen nicht verwarnt werden!", ephemeral=True)
        warns = load_data("warnings.json"); uid = str(user.id)
        if uid not in warns: warns[uid] = []
        warns[uid].append({"reason":grund,"mod":str(interaction.user.id),"time":datetime.datetime.utcnow().isoformat()})
        save_data("warnings.json", warns)
        e = discord.Embed(title="⚠️ User verwarnt", color=discord.Color.yellow())
        e.set_thumbnail(url=user.display_avatar.url)
        e.add_field(name="User",value=user.mention,inline=True)
        e.add_field(name="Verwarnungen",value=str(len(warns[uid])),inline=True)
        e.add_field(name="Grund",value=grund,inline=False)
        await interaction.response.send_message(embed=e)
        await self._log(interaction.guild,"WARN",user,interaction.user,grund)

    @app_commands.command(name="warns", description="Zeigt alle Verwarnungen eines Users")
    @app_commands.describe(user="User")
    @app_commands.default_permissions(moderate_members=True)
    async def warns(self, interaction: discord.Interaction, user: discord.Member):
        uw = load_data("warnings.json").get(str(user.id), [])
        e  = discord.Embed(title=f"⚠️ Verwarnungen: {user.display_name}", color=discord.Color.orange())
        e.set_thumbnail(url=user.display_avatar.url)
        if not uw:
            e.description = "✅ Keine Verwarnungen."
        else:
            for i, w in enumerate(uw, 1):
                e.add_field(name=f"#{i} — {w.get('time','')[:10]}", value=w["reason"], inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="clearwarns", description="Loescht alle Verwarnungen eines Users")
    @app_commands.describe(user="User")
    @app_commands.default_permissions(administrator=True)
    async def clearwarns(self, interaction: discord.Interaction, user: discord.Member):
        w = load_data("warnings.json"); w[str(user.id)] = []; save_data("warnings.json", w)
        await interaction.response.send_message(f"✅ Verwarnungen von {user.mention} geloescht!", ephemeral=True)

    @app_commands.command(name="clear", description="Loescht Nachrichten im Channel (max 100)")
    @app_commands.describe(anzahl="Anzahl (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, anzahl: int = 10):
        if not 1 <= anzahl <= 100:
            return await interaction.response.send_message("❌ 1–100!", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=anzahl)
        await interaction.followup.send(f"✅ {len(deleted)} Nachrichten geloescht!", ephemeral=True)

    @app_commands.command(name="slowmode", description="Setzt den Slowmode im Channel (0 = aus)")
    @app_commands.describe(sekunden="Sekunden (0-21600)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, sekunden: int = 0):
        if not 0 <= sekunden <= 21600:
            return await interaction.response.send_message("❌ 0–21600 Sekunden!", ephemeral=True)
        await interaction.channel.edit(slowmode_delay=sekunden)
        msg = "✅ Slowmode deaktiviert!" if sekunden == 0 else f"✅ Slowmode: **{sekunden} Sekunden**"
        await interaction.response.send_message(msg)


async def setup(bot): await bot.add_cog(Moderation(bot))
