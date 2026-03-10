import os

def write_cog(name, classname, content):
    path = f'cogs/{name}.py'
    template = f"import discord\nfrom discord.ext import commands\n\nclass {classname}(commands.Cog):\n    def __init__(self, bot):\n        self.bot = bot\n\n{content}\n\nasync def setup(bot):\n    await bot.add_cog({classname}(bot))"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(template)

os.makedirs('cogs', exist_ok=True)

# HIER IST DIE ECHTE LOGIK FÜR JEDE DATEI
write_cog('addrole', 'AddRole', '    @commands.hybrid_command(name="addrole", description="Gibt eine Rolle")\n    @commands.has_permissions(manage_roles=True)\n    async def addrole(self, ctx, member: discord.Member, role: discord.Role):\n        await member.add_roles(role)\n        await ctx.send(f"✅ Rolle {role.mention} an {member.mention} vergeben!")')

write_cog('ban', 'Ban', '    @commands.hybrid_command(name="ban", description="Sperrt einen User")\n    @commands.has_permissions(ban_members=True)\n    async def ban(self, ctx, member: discord.Member, *, grund="Kein Grund"): \n        await member.ban(reason=grund)\n        await ctx.send(f"🚫 {member.name} wurde gebannt. Grund: {grund}")')

write_cog('clear', 'Clear', '    @commands.hybrid_command(name="clear", description="Löscht Nachrichten")\n    @commands.has_permissions(manage_messages=True)\n    async def clear(self, ctx, anzahl: int):\n        await ctx.channel.purge(limit=anzahl)\n        await ctx.send(f"🧹 {anzahl} Nachrichten gelöscht.", delete_after=3)')

write_cog('help', 'Help', '    @commands.hybrid_command(name="help", description="Hilfe-Menü")\n    async def help(self, ctx):\n        embed = discord.Embed(title="⚡ Neon Bot Hilfe", color=0x00ffff)\n        embed.add_field(name="🛡️ Moderation", value="an, kick, mute, unmute, clear, 
uke, slowmode")\n        embed.add_field(name="⚙️ Admin", value="lock, unlock, ddrole, 
ick, settings")\n        embed.add_field(name="🔗 Kontakt", value="🌐 [Website](https://neon-bot-2026.vercel.app/)\\n📧 dev-jojo@proton.me")\n        await ctx.send(embed=embed)')

write_cog('avatar', 'Avatar', '    @commands.hybrid_command(name="avatar", description="Zeigt das Profilbild")\n    async def avatar(self, ctx, member: discord.Member = None):\n        member = member or ctx.author\n        await ctx.send(member.display_avatar.url)')

write_cog('ping', 'Ping', '    @commands.hybrid_command(name="ping", description="Prüft die Latenz")\n    async def ping(self, ctx):\n        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")')

write_cog('mute', 'Mute', '    @commands.hybrid_command(name="mute", description="User stummschalten")\n    @commands.has_permissions(moderate_members=True)\n    async def mute(self, ctx, member: discord.Member, minuten: int = 10):\n        import datetime\n        await member.timeout(datetime.timedelta(minutes=minuten))\n        await ctx.send(f"🔇 {member.mention} für {minuten} Min gemutet.")')

# Wir erstellen für alle anderen Bilder-Dateien saubere Grundgerüste
others = ["automod", "kick", "level_system", "link_filter", "lock", "logging_event", "logging", "nick", "nuke", "owner", "removerole", "serverinfo", "settings", "slowmode", "softban", "test_cmd", "unban", "unlock", "unmute", "userinfo", "vckick", "vcmute", "vcunmute", "welcome", "welcome_event", "whitelist"]
for o in others:
    write_cog(o, o.title().replace("_",""), f'    @commands.hybrid_command(name="{o}", description="Befehl {o}")\n    async def {o}(self, ctx): await ctx.send("🛠️ Dieser Befehl ({o}) wird gerade überarbeitet.")')

print("Alle 33 Dateien wurden sauber erstellt!")
