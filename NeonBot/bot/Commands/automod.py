import discord
from discord.ext import commands
from discord import app_commands
import re, datetime
from Commands.helper import load_data, save_data

DEFAULT_BADWORDS = [
    "hurensohn", "wichser", "scheiße", "scheisse", "arschloch",
    "vollidiot", "idiot", "blödmann", "blodmann", "fick",
    "fotze", "nutte", "bastard", "schlampe",
]

def is_enabled(guild_id, module):
    return load_data("config.json").get(str(guild_id), {}).get(f"module_{module}", False)

def get_badwords(guild_id):
    custom = load_data("config.json").get(str(guild_id), {}).get("badwords", [])
    return list(set(DEFAULT_BADWORDS + [w.lower() for w in custom]))

def get_consequences(guild_id):
    return load_data("config.json").get(str(guild_id), {}).get("automod_consequences", {
        "warn_after": 3, "mute_after": 5, "kick_after": 8,
        "ban_after": 10, "mute_duration": 10
    })

def add_violation(guild_id, user_id):
    v = load_data("automod_violations.json")
    gid, uid = str(guild_id), str(user_id)
    if gid not in v: v[gid] = {}
    if uid not in v[gid]: v[gid][uid] = 0
    v[gid][uid] += 1
    save_data("automod_violations.json", v)
    return v[gid][uid]

def reset_violations(guild_id, user_id):
    v = load_data("automod_violations.json")
    gid, uid = str(guild_id), str(user_id)
    if gid in v and uid in v[gid]:
        v[gid][uid] = 0
        save_data("automod_violations.json", v)

async def send_dm(user, embed):
    try: await user.send(embed=embed)
    except: pass

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        if not is_enabled(message.guild.id, "automod"): return
        if message.author.guild_permissions.administrator: return
        if message.author.guild_permissions.manage_messages: return

        content  = message.content.lower()
        gid      = message.guild.id
        user     = message.author
        triggered, reason = False, None

        for word in get_badwords(gid):
            if word in content:
                triggered, reason = True, "Verbotenes Wort verwendet"
                break

        if not triggered and re.search(r"discord\.(gg|com/invite)/[a-zA-Z0-9\-]+", content):
            triggered, reason = True, "Discord Invite Link"

        if not triggered and len(message.mentions) > 5:
            triggered, reason = True, f"Massen-Ping ({len(message.mentions)} User)"

        if not triggered and len(content) > 10:
            letters = [c for c in content if c.isalpha()]
            if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.7:
                triggered, reason = True, "Caps-Lock Spam"

        if not triggered: return

        try: await message.delete()
        except: return

        count        = add_violation(gid, user.id)
        cons         = get_consequences(gid)
        warn_at      = cons["warn_after"]
        mute_at      = cons["mute_after"]
        kick_at      = cons["kick_after"]
        ban_at       = cons["ban_after"]
        mute_dur     = cons["mute_duration"]
        action_taken = None

        dm = discord.Embed(title=f"⚠️ AutoMod — {message.guild.name}", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
        dm.add_field(name="Grund",    value=reason,        inline=False)
        dm.add_field(name="Verstoesse", value=str(count),  inline=True)

        if count >= ban_at:
            action_taken = "ban"
            dm.add_field(name="🔨 Konsequenz", value=f"Du wurdest gebannt! ({count} Verstoesse)", inline=False)
            dm.color = discord.Color.red()
        elif count >= kick_at:
            action_taken = "kick"
            dm.add_field(name="👢 Konsequenz", value=f"Du wurdest gekickt! ({count} Verstoesse)", inline=False)
            dm.color = discord.Color.red()
        elif count >= mute_at:
            action_taken = "mute"
            dm.add_field(name="🔇 Konsequenz", value=f"Du wurdest {mute_dur} Min gemutet! ({count} Verstoesse)", inline=False)
            dm.color = discord.Color.yellow()
        elif count >= warn_at:
            action_taken = "warn"
            dm.add_field(name="⚠️ Konsequenz", value=f"Du hast eine Verwarnung erhalten! ({count} Verstoesse)", inline=False)
        else:
            dm.add_field(name="ℹ️ Hinweis", value=f"Noch {warn_at - count} Verstoesse bis zur naechsten Konsequenz.", inline=False)

        dm.set_footer(text=f"Neon Bot AutoMod • {message.guild.name}")
        await send_dm(user, dm)

        ar = f"AutoMod: {reason} ({count} Verstoesse)"
        try:
            if action_taken == "warn":
                warns = load_data("warnings.json")
                uid   = str(user.id)
                if uid not in warns: warns[uid] = []
                warns[uid].append({"reason": f"AutoMod: {reason}", "mod": "AutoMod", "time": datetime.datetime.utcnow().isoformat()})
                save_data("warnings.json", warns)
            elif action_taken == "mute":
                from datetime import timedelta
                await user.timeout(timedelta(minutes=mute_dur), reason=ar)
            elif action_taken == "kick":
                await user.kick(reason=ar); reset_violations(gid, user.id)
            elif action_taken == "ban":
                await user.ban(reason=ar, delete_message_days=1); reset_violations(gid, user.id)
        except discord.Forbidden: pass

        cfg    = load_data("config.json")
        log_id = cfg.get(str(gid), {}).get("log_channel")
        if log_id:
            log_ch = message.guild.get_channel(int(log_id))
            if log_ch:
                le = discord.Embed(title="🛡️ AutoMod — Verstoss", color=discord.Color.red() if action_taken in ["ban","kick"] else discord.Color.orange(), timestamp=datetime.datetime.utcnow())
                le.set_thumbnail(url=user.display_avatar.url)
                le.add_field(name="User",    value=f"{user.mention} (`{user.id}`)", inline=True)
                le.add_field(name="Channel", value=message.channel.mention,         inline=True)
                le.add_field(name="Grund",   value=reason,                          inline=False)
                le.add_field(name="Verstoesse", value=str(count),                   inline=True)
                if action_taken:
                    le.add_field(name="Konsequenz", value={"warn":"⚠️ Verwarnt","mute":f"🔇 Gemutet ({mute_dur} Min)","kick":"👢 Gekickt","ban":"🔨 Gebannt"}[action_taken], inline=True)
                le.add_field(name="Nachricht", value=f"```{message.content[:200]}```", inline=False)
                await log_ch.send(embed=le)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot or not after.guild: return
        if not is_enabled(after.guild.id, "automod"): return
        await self.on_message(after)

    @app_commands.command(name="addword", description="Fuegt ein Wort zur Blacklist hinzu")
    @app_commands.default_permissions(administrator=True)
    async def addword(self, interaction: discord.Interaction, word: str):
        config = load_data("config.json")
        gid    = str(interaction.guild.id)
        if gid not in config: config[gid] = {}
        if "badwords" not in config[gid]: config[gid]["badwords"] = []
        word = word.lower().strip()
        if word in config[gid]["badwords"]:
            return await interaction.response.send_message(f"❌ `{word}` ist bereits in der Blacklist!", ephemeral=True)
        config[gid]["badwords"].append(word)
        save_data("config.json", config)
        await interaction.response.send_message(f"✅ `{word}` zur Blacklist hinzugefuegt!", ephemeral=True)

    @app_commands.command(name="removeword", description="Entfernt ein Wort aus der Blacklist")
    @app_commands.default_permissions(administrator=True)
    async def removeword(self, interaction: discord.Interaction, word: str):
        config = load_data("config.json")
        gid    = str(interaction.guild.id)
        word   = word.lower().strip()
        words  = config.get(gid, {}).get("badwords", [])
        if word not in words:
            return await interaction.response.send_message(f"❌ `{word}` nicht in der Blacklist!", ephemeral=True)
        words.remove(word)
        config[gid]["badwords"] = words
        save_data("config.json", config)
        await interaction.response.send_message(f"✅ `{word}` entfernt!", ephemeral=True)

    @app_commands.command(name="blacklist", description="Zeigt alle verbotenen Woerter")
    @app_commands.default_permissions(administrator=True)
    async def blacklist(self, interaction: discord.Interaction):
        config = load_data("config.json")
        custom = config.get(str(interaction.guild.id), {}).get("badwords", [])
        embed  = discord.Embed(title="🚫 Blacklist", color=discord.Color.red())
        embed.add_field(name=f"Standard ({len(DEFAULT_BADWORDS)})", value="`" + "`, `".join(DEFAULT_BADWORDS) + "`", inline=False)
        embed.add_field(name=f"Custom ({len(custom)})",             value="`" + "`, `".join(custom) + "`" if custom else "*Keine*", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setconsequences", description="Konsequenzen fuer AutoMod einstellen")
    @app_commands.describe(warn_after="Verstoesse bis Warn", mute_after="Verstoesse bis Mute", kick_after="Verstoesse bis Kick", ban_after="Verstoesse bis Ban", mute_duration="Mute Dauer in Minuten")
    @app_commands.default_permissions(administrator=True)
    async def setconsequences(self, interaction: discord.Interaction, warn_after: int = 3, mute_after: int = 5, kick_after: int = 8, ban_after: int = 10, mute_duration: int = 10):
        if not (warn_after < mute_after < kick_after < ban_after):
            return await interaction.response.send_message("❌ Reihenfolge muss sein: Warn < Mute < Kick < Ban!", ephemeral=True)
        config = load_data("config.json")
        gid    = str(interaction.guild.id)
        if gid not in config: config[gid] = {}
        config[gid]["automod_consequences"] = {"warn_after": warn_after, "mute_after": mute_after, "kick_after": kick_after, "ban_after": ban_after, "mute_duration": mute_duration}
        save_data("config.json", config)
        e = discord.Embed(title="✅ Konsequenzen gespeichert", color=discord.Color.green())
        e.add_field(name="⚠️ Warn",  value=f"ab {warn_after}",                    inline=True)
        e.add_field(name="🔇 Mute",  value=f"ab {mute_after} ({mute_duration} Min)", inline=True)
        e.add_field(name="👢 Kick",  value=f"ab {kick_after}",                    inline=True)
        e.add_field(name="🔨 Ban",   value=f"ab {ban_after}",                     inline=True)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="violations", description="Verstoesse eines Users anzeigen")
    @app_commands.default_permissions(moderate_members=True)
    async def violations(self, interaction: discord.Interaction, user: discord.Member):
        v     = load_data("automod_violations.json")
        count = v.get(str(interaction.guild.id), {}).get(str(user.id), 0)
        cons  = get_consequences(interaction.guild.id)
        e     = discord.Embed(title=f"📊 Verstoesse: {user.display_name}", color=discord.Color.orange())
        e.set_thumbnail(url=user.display_avatar.url)
        e.add_field(name="Verstoesse", value=str(count), inline=True)
        next_a = "✅ Keine"
        if   count < cons["warn_after"]: next_a = f"⚠️ Warn bei {cons['warn_after']}"
        elif count < cons["mute_after"]: next_a = f"🔇 Mute bei {cons['mute_after']}"
        elif count < cons["kick_after"]: next_a = f"👢 Kick bei {cons['kick_after']}"
        elif count < cons["ban_after"]:  next_a = f"🔨 Ban bei {cons['ban_after']}"
        e.add_field(name="Naechste Konsequenz", value=next_a, inline=True)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="resetviolations", description="Verstoesse eines Users zuruecksetzen")
    @app_commands.default_permissions(administrator=True)
    async def resetviolations(self, interaction: discord.Interaction, user: discord.Member):
        reset_violations(interaction.guild.id, user.id)
        await interaction.response.send_message(f"✅ Verstoesse von {user.mention} zurueckgesetzt!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
