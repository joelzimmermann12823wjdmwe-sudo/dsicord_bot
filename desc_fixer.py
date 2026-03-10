import os

def write_cog(name, classname, content):
    os.makedirs('cogs', exist_ok=True)
    with open(f'cogs/{name}.py', 'w', encoding='utf-8') as f:
        f.write(f"""import discord
from discord.ext import commands
import datetime

class {classname}(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

{content}

async def setup(bot):
    await bot.add_cog({classname}(bot))""")

# --- MODERATION ---
write_cog('ban', 'Ban', """    @commands.hybrid_command(name="ban", description="Sperrt einen Nutzer permanent vom Server.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Kein Grund"):
        await member.ban(reason=reason)
        await ctx.send(f"🚫 {member.name} gebannt.")""")

write_cog('kick', 'Kick', """    @commands.hybrid_command(name="kick", description="Wirft einen Nutzer vom Server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Kein Grund"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.name} gekickt.")""")

write_cog('mute', 'Mute', """    @commands.hybrid_command(name="mute", description="Schaltet einen Nutzer für eine bestimmte Zeit stumm.")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minuten: int = 10):
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=minuten))
        await ctx.send(f"🔇 {member.name} für {minuten}m stummgeschaltet.")""")

write_cog('unmute', 'Unmute', """    @commands.hybrid_command(name="unmute", description="Hebt die Stummschaltung eines Nutzers auf.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 {member.name} wurde entmutet.")""")

write_cog('clear', 'Clear', """    @commands.hybrid_command(name="clear", description="Löscht eine bestimmte Anzahl an Nachrichten im Kanal.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, anzahl: int):
        await ctx.channel.purge(limit=anzahl)
        await ctx.send(f"🧹 {anzahl} Nachrichten gelöscht.", delete_after=3)""")

write_cog('softban', 'Softban', """    @commands.hybrid_command(name="softban", description="Bannt und entbannt sofort (löscht die Nachrichten des Nutzers).")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member):
        await member.ban(reason="Softban")
        await member.unban()
        await ctx.send(f"🍦 Softban für {member.name} erfolgreich.")""")

write_cog('unban', 'Unban', """    @commands.hybrid_command(name="unban", description="Entbannt einen zuvor gesperrten Nutzer per ID.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str):
        user = await self.bot.fetch_user(int(user_id))
        await ctx.guild.unban(user)
        await ctx.send(f"🔓 {user.name} erfolgreich entbannt.")""")


# --- ADMIN & SERVER ---
write_cog('addrole', 'Addrole', """    @commands.hybrid_command(name="addrole", description="Weist einem Nutzer eine bestimmte Rolle zu.")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f"✅ {member.name} hat nun die Rolle {role.name}.")""")

write_cog('removerole', 'Removerole', """    @commands.hybrid_command(name="removerole", description="Entfernt eine bestimmte Rolle von einem Nutzer.")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        await ctx.send(f"❌ {member.name} wurde die Rolle {role.name} entfernt.")""")

write_cog('lock', 'Lock', """    @commands.hybrid_command(name="lock", description="Sperrt den aktuellen Kanal für normale Nachrichten.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Dieser Kanal ist nun gesperrt.")""")

write_cog('unlock', 'Unlock', """    @commands.hybrid_command(name="unlock", description="Entsperrt den aktuellen Kanal wieder.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Dieser Kanal ist wieder entsperrt.")""")

write_cog('slowmode', 'Slowmode', """    @commands.hybrid_command(name="slowmode", description="Setzt eine Abklingzeit für Nachrichten in Sekunden.")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, sekunden: int):
        await ctx.channel.edit(slowmode_delay=sekunden)
        await ctx.send(f"⏳ Slowmode auf {sekunden} Sekunden gesetzt.")""")

write_cog('nick', 'Nick', """    @commands.hybrid_command(name="nick", description="Ändert den Nicknamen eines Nutzers auf dem Server.")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, name: str):
        await member.edit(nick=name)
        await ctx.send(f"📝 Nickname geändert zu {name}.")""")

write_cog('nuke', 'Nuke', """    @commands.hybrid_command(name="nuke", description="Löscht den Kanal und erstellt ihn komplett neu (Achtung!).")
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        pos = ctx.channel.position
        new = await ctx.channel.clone()
        await ctx.channel.delete()
        await new.edit(position=pos)
        await new.send("☢️ Kanal wurde gesprengt und erneuert.")""")

write_cog('settings', 'Settings', """    @commands.hybrid_command(name="settings", description="Öffnet das Einstellungsmenü des Bots.")
    async def settings(self, ctx):
        await ctx.send("⚙️ Einstellungen: Bald verfügbar!")""")

write_cog('whitelist', 'Whitelist', """    @commands.hybrid_command(name="whitelist", description="Zeigt den Status der Bot-Whitelist.")
    async def whitelist(self, ctx):
        await ctx.send("⚪ Whitelist-System ist aktiv.")""")


# --- USER & INFO ---
write_cog('avatar', 'Avatar', """    @commands.hybrid_command(name="avatar", description="Zeigt das Profilbild (Avatar) eines Nutzers in groß.")
    async def avatar(self, ctx, member: discord.Member=None):
        member = member or ctx.author
        await ctx.send(member.display_avatar.url)""")

write_cog('userinfo', 'Userinfo', """    @commands.hybrid_command(name="userinfo", description="Zeigt detaillierte Informationen über einen Nutzer an.")
    async def userinfo(self, ctx, member: discord.Member=None):
        member = member or ctx.author
        e = discord.Embed(title=f"User Info: {member.name}", color=member.color)
        e.add_field(name="ID", value=member.id)
        e.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=e)""")

write_cog('serverinfo', 'Serverinfo', """    @commands.hybrid_command(name="serverinfo", description="Zeigt nützliche Statistiken und Infos über diesen Server.")
    async def serverinfo(self, ctx):
        g = ctx.guild
        e = discord.Embed(title=f"Server Info: {g.name}", color=0x00ffff)
        e.add_field(name="Mitglieder", value=g.member_count)
        await ctx.send(embed=e)""")

write_cog('ping', 'Ping', """    @commands.hybrid_command(name="ping", description="Zeigt die aktuelle Reaktionszeit (Latenz) des Bots an.")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")""")

write_cog('help', 'Help', """    @commands.hybrid_command(name="help", description="Zeigt eine Übersicht aller verfügbaren Befehle.")
    async def help(self, ctx):
        e = discord.Embed(title="⚡ Neon Bot Hilfe", color=0x00ffff)
        e.add_field(name="🌐 Website", value="[Neon Bot Dashboard](https://neon-bot-2026.vercel.app/)")
        await ctx.send(embed=e)""")

write_cog('welcome', 'Welcome', """    @commands.hybrid_command(name="welcome_test", description="Testet die Willkommensnachricht manuell.")
    async def welcome_test(self, ctx):
        await ctx.send("👋 Test: Willkommen auf dem Server!")""")

write_cog('test_cmd', 'TestCmd', """    @commands.hybrid_command(name="test", description="Ein einfacher Test-Befehl zur Funktionsprüfung.")
    async def test(self, ctx):
        await ctx.send("🚀 Alles funktioniert super!")""")


# --- VOICE ---
write_cog('vckick', 'Vckick', """    @commands.hybrid_command(name="vckick", description="Wirft einen Nutzer aus seinem aktuellen Sprachkanal.")
    @commands.has_permissions(move_members=True)
    async def vckick(self, ctx, member: discord.Member):
        if member.voice:
            await member.move_to(None)
            await ctx.send(f"👢 {member.name} aus dem Voice gekickt.")
        else:
            await ctx.send("Dieser Nutzer ist nicht im Voice-Channel.")""")

write_cog('vcmute', 'Vcmute', """    @commands.hybrid_command(name="vcmute", description="Schaltet das Mikrofon eines Nutzers im Sprachkanal stumm.")
    @commands.has_permissions(mute_members=True)
    async def vcmute(self, ctx, member: discord.Member):
        await member.edit(mute=True)
        await ctx.send(f"🔇 {member.name} im Voice gemutet.")""")

write_cog('vcunmute', 'Vcunmute', """    @commands.hybrid_command(name="vcunmute", description="Entmutet das Mikrofon eines Nutzers im Sprachkanal.")
    @commands.has_permissions(mute_members=True)
    async def vcunmute(self, ctx, member: discord.Member):
        await member.edit(mute=False)
        await ctx.send(f"🔊 {member.name} im Voice entmutet.")""")


# --- BACKEND / LISTENERS (Diese haben keinen Chat-Befehl und brauchen keine Beschreibung) ---
write_cog('owner', 'Owner', """    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("💤 Fahre herunter...")
        await self.bot.close()""")

write_cog('automod', 'Automod', """    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return
        if "discord.gg/" in msg.content.lower():
            await msg.delete()
            await msg.channel.send("🚫 Keine Werbung!", delete_after=3)""")

write_cog('link_filter', 'LinkFilter', """    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return
        if "http" in msg.content and not msg.author.guild_permissions.administrator:
            await msg.delete()
            await msg.channel.send("🔗 Links sind verboten!", delete_after=3)""")

write_cog('logging', 'Logging', """    @commands.Cog.listener()
    async def on_message_delete(self, m):
        ch = discord.utils.get(m.guild.channels, name="logs")
        if ch:
            await ch.send(f"🗑️ Gelöscht in {m.channel.mention}: {m.content} von {m.author}")""")

write_cog('logging_event', 'LoggingEvent', """    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        pass""")

write_cog('welcome_event', 'WelcomeEvent', """    @commands.Cog.listener()
    async def on_member_join(self, m):
        ch = discord.utils.get(m.guild.channels, name="welcome")
        if ch:
            await ch.send(f"👋 Willkommen {m.mention}!")""")

write_cog('level_system', 'LevelSystem', """    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot: return
        # Platzhalter für Datenbank-Logik
        pass""")

print("✅ Alle Beschreibungen erfolgreich hinzugefügt!")
