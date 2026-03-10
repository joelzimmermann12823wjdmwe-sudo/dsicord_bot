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
write_cog('ban', 'Ban', """    @commands.hybrid_command(name="ban", description="Sperrt einen Nutzer")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, grund="Kein Grund"):
        await member.ban(reason=grund)
        await ctx.send(f"🚫 **{member.name}** wurde gesperrt. | Grund: {grund}")""")

write_cog('kick', 'Kick', """    @commands.hybrid_command(name="kick", description="Kickt einen Nutzer")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, grund="Kein Grund"):
        await member.kick(reason=grund)
        await ctx.send(f"👢 **{member.name}** wurde gekickt. | Grund: {grund}")""")

write_cog('mute', 'Mute', """    @commands.hybrid_command(name="mute", description="Stummschaltung")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minuten: int = 10):
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=minuten))
        await ctx.send(f"🔇 **{member.mention}** wurde für {minuten} Minuten stummgeschaltet.")""")

write_cog('unmute', 'Unmute', """    @commands.hybrid_command(name="unmute", description="Stummschaltung aufheben")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 Stummschaltung für **{member.mention}** aufgehoben.")""")

write_cog('clear', 'Clear', """    @commands.hybrid_command(name="clear", description="Löscht Nachrichten")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, anzahl: int):
        await ctx.channel.purge(limit=anzahl)
        await ctx.send(f"🧹 **{anzahl}** Nachrichten wurden gelöscht.", delete_after=3)""")

write_cog('nuke', 'Nuke', """    @commands.hybrid_command(name="nuke", description="Erneuert den Kanal")
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        pos = ctx.channel.position
        new = await ctx.channel.clone()
        await ctx.channel.delete()
        await new.edit(position=pos)
        await new.send("☢️ Kanal erfolgreich gesprengt und erneuert!")""")

# --- ADMIN ---
write_cog('lock', 'Lock', """    @commands.hybrid_command(name="lock", description="Sperrt den Kanal")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Dieser Kanal wurde gesperrt.")""")

write_cog('unlock', 'Unlock', """    @commands.hybrid_command(name="unlock", description="Entsperrt den Kanal")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Dieser Kanal wurde entsperrt.")""")

write_cog('addrole', 'AddRole', """    @commands.hybrid_command(name="addrole", description="Gibt eine Rolle")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f"✅ Rolle {role.mention} an {member.mention} vergeben.")""")

write_cog('removerole', 'RemoveRole', """    @commands.hybrid_command(name="removerole", description="Entfernt eine Rolle")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)
        await ctx.send(f"❌ Rolle {role.name} von {member.name} entfernt.")""")

# --- INFO & USER ---
write_cog('help', 'Help', """    @commands.hybrid_command(name="help", description="Hilfe-Menü")
    async def help(self, ctx):
        embed = discord.Embed(title="⚡ Neon Bot Hilfe", color=0x00ffff)
        embed.add_field(name="🛡️ Moderation", value="`ban`, `kick`, `mute`, `unmute`, `clear`, `nuke`, `softban`.", inline=False)
        embed.add_field(name="⚙️ Admin", value="`lock`, `unlock`, `addrole`, `removerole`, `nick`, `slowmode`.", inline=False)
        embed.add_field(name="🔗 Kontakt", value="🌐 [Website](https://neon-bot-2026.vercel.app/)\\n📧 dev-jojo@proton.me", inline=False)
        embed.set_footer(text="Nutze !help oder /help")
        await ctx.send(embed=embed)""")

write_cog('avatar', 'Avatar', """    @commands.hybrid_command(name="avatar", description="Zeigt das Profilbild")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(member.display_avatar.url)""")

write_cog('ping', 'Ping', """    @commands.hybrid_command(name="ping", description="Prüft die Latenz")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")""")

write_cog('serverinfo', 'ServerInfo', """    @commands.hybrid_command(name="serverinfo", description="Infos zum Server")
    async def serverinfo(self, ctx):
        g = ctx.guild
        embed = discord.Embed(title=f"Serverinfo: {g.name}", color=0x00ffff)
        embed.add_field(name="Mitglieder", value=g.member_count)
        embed.add_field(name="Erstellt am", value=g.created_at.strftime('%d.%m.%Y'))
        await ctx.send(embed=embed)""")

# --- VOICE ---
write_cog('vckick', 'VCKick', """    @commands.hybrid_command(name="vckick", description="Kickt aus dem Voice")
    @commands.has_permissions(move_members=True)
    async def vckick(self, ctx, member: discord.Member):
        if member.voice:
            await member.move_to(None)
            await ctx.send(f"🔇 {member.name} aus dem Voice gekickt.")""")

# --- ALLE WEITEREN DATEIEN (Dummies) ---
others = ["automod", "level_system", "link_filter", "logging_event", "logging", "nick", "owner", "settings", "slowmode", "softban", "test_cmd", "unban", "userinfo", "vcmute", "vcunmute", "welcome", "welcome_event", "whitelist"]
for o in others:
    write_cog(o, o.replace("_","").title(), f'    @commands.hybrid_command(name="{o}", description="Befehl {o}")\\n    async def {o}(self, ctx): await ctx.send("🛠️ Dieser Befehl ist aktiv, die Logik folgt bald!")')

print("✅ Alle 33 Dateien wurden perfekt generiert!")
