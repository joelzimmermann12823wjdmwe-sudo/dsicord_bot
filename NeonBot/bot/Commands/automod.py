import discord
import datetime
import re
from datetime import timedelta
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data, is_module_enabled, get_log_channel_id

# Standard-Blacklist (deutsch)
DEFAULT_BADWORDS = [
    "hurensohn", "wichser", "scheiße", "scheisse", "arschloch",
    "vollidiot", "idiot", "blödmann", "blodmann",
    "fick", "ficker", "fotze", "nutte", "bastard", "schlampe",
    "dummkopf", "trottel", "depp", "vollidiot", "missgeburt",
]

def get_badwords(guild_id: int) -> list:
    custom = load_data("config.json").get(str(guild_id), {}).get("badwords", [])
    return list(set(DEFAULT_BADWORDS + [w.lower().strip() for w in custom]))

def get_consequences(guild_id: int) -> dict:
    default = {
        "warn_after":    3,
        "mute_after":    5,
        "kick_after":    8,
        "ban_after":     10,
        "mute_duration": 10,
    }
    saved = load_data("config.json").get(str(guild_id), {}).get("automod_consequences", {})
    default.update(saved)
    return default

def add_violation(guild_id: int, user_id: int) -> int:
    v   = load_data("automod_violations.json")
    g   = str(guild_id)
    u   = str(user_id)
    if g not in v:
        v[g] = {}
    v[g][u] = int(v[g].get(u, 0)) + 1
    count   = v[g][u]
    save_data("automod_violations.json", v)
    return count

def get_violations(guild_id: int, user_id: int) -> int:
    return int(load_data("automod_violations.json").get(str(guild_id), {}).get(str(user_id), 0))

def reset_violations(guild_id: int, user_id: int):
    v = load_data("automod_violations.json")
    g = str(guild_id)
    u = str(user_id)
    if g in v:
        v[g][u] = 0
    save_data("automod_violations.json", v)

async def try_dm(user: discord.Member, embed: discord.Embed):
    """DM senden — Fehler werden ignoriert (DMs koennen gesperrt sein)"""
    try:
        await user.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        pass  # User hat DMs deaktiviert — kein Problem

async def send_log(guild: discord.Guild, embed: discord.Embed):
    """Log in den konfigurierten Log-Channel senden"""
    ch_id = get_log_channel_id(guild.id)
    if not ch_id:
        return
    ch = guild.get_channel(int(ch_id))
    if ch:
        try:
            await ch.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_message(self, message: discord.Message):
        """Kern-Funktion: Nachricht pruefen und reagieren"""

        # Basisprüfungen
        if not message.guild:               return
        if message.author.bot:              return
        if not message.content:             return

        # Modul-Check — Standard ist False = deaktiviert
        # Aktivieren mit /automod on oder /setlog (setzt automatisch auf True)
        if not is_module_enabled(message.guild.id, "automod"):
            return

        # Moderatoren und Admins sind ausgenommen
        member = message.author
        if member.guild_permissions.administrator:    return
        if member.guild_permissions.manage_messages:  return
        if member.guild_permissions.manage_guild:     return

        content  = message.content.lower()
        guild_id = message.guild.id
        triggered = False
        reason    = None

        # ── Check 1: Schimpfwörter ──────────────────────
        for word in get_badwords(guild_id):
            if word in content:
                triggered = True
                reason    = f"Verbotenes Wort: `{word}`"
                break

        # ── Check 2: Invite-Links ───────────────────────
        if not triggered:
            if re.search(r"discord\.(gg|com/invite)/[a-zA-Z0-9\-]+", content):
                triggered = True
                reason    = "Discord Invite-Link gesendet"

        # ── Check 3: Massen-Pings ───────────────────────
        if not triggered:
            if len(message.mentions) > 5:
                triggered = True
                reason    = f"Massen-Ping ({len(message.mentions)} User)"

        # ── Check 4: Caps-Spam ──────────────────────────
        if not triggered and len(content) > 15:
            letters = [c for c in content if c.isalpha()]
            if letters and (sum(1 for c in letters if c.isupper()) / len(letters)) > 0.75:
                triggered = True
                reason    = "Caps-Spam"

        if not triggered:
            return

        # ── Nachricht löschen ────────────────────────────
        try:
            await message.delete()
        except (discord.NotFound, discord.Forbidden):
            return  # Nachricht schon weg oder keine Rechte

        # ── Verstoß zählen ───────────────────────────────
        count = add_violation(guild_id, member.id)
        cons  = get_consequences(guild_id)

        warn_at  = cons["warn_after"]
        mute_at  = cons["mute_after"]
        kick_at  = cons["kick_after"]
        ban_at   = cons["ban_after"]
        mute_dur = cons["mute_duration"]

        # ── Konsequenz bestimmen ─────────────────────────
        action = None
        if   count >= ban_at:  action = "ban"
        elif count >= kick_at: action = "kick"
        elif count >= mute_at: action = "mute"
        elif count >= warn_at: action = "warn"

        # ── DM an User ───────────────────────────────────
        dm = discord.Embed(
            title    = f"⚠️ AutoMod — {message.guild.name}",
            color    = discord.Color.red() if action in ("ban","kick") else discord.Color.orange(),
            timestamp = datetime.datetime.utcnow()
        )
        dm.add_field(name="Grund",       value=reason,      inline=False)
        dm.add_field(name="Verstöße",    value=str(count),  inline=True)
        dm.add_field(name="Channel",     value=message.channel.mention, inline=True)

        action_labels = {
            "warn": f"⚠️ Du hast eine Verwarnung erhalten! ({count}/{warn_at})",
            "mute": f"🔇 Du wurdest für {mute_dur} Minuten gemutet! ({count}/{mute_at})",
            "kick": f"👢 Du wurdest vom Server gekickt! ({count}/{kick_at})",
            "ban":  f"🔨 Du wurdest permanent gebannt! ({count}/{ban_at})",
        }
        if action:
            dm.add_field(name="Konsequenz", value=action_labels[action], inline=False)
        else:
            remaining = warn_at - count
            dm.add_field(
                name  = "ℹ️ Hinweis",
                value = f"Noch **{remaining}** Verstoß/Verstöße bis zur Verwarnung.",
                inline = False
            )
        dm.set_footer(text=f"Neon Bot • AutoMod")

        await try_dm(member, dm)

        # ── Konsequenz ausführen ─────────────────────────
        ar = f"AutoMod: {reason} ({count} Verstöße)"
        try:
            if action == "warn":
                warns = load_data("warnings.json")
                uid   = str(member.id)
                if uid not in warns:
                    warns[uid] = []
                warns[uid].append({
                    "reason": f"AutoMod: {reason}",
                    "mod":    "AutoMod",
                    "time":   datetime.datetime.utcnow().isoformat()
                })
                save_data("warnings.json", warns)

            elif action == "mute":
                # timedelta kommt aus datetime, NICHT aus discord!
                await member.timeout(timedelta(minutes=mute_dur), reason=ar)

            elif action == "kick":
                await member.kick(reason=ar)
                reset_violations(guild_id, member.id)

            elif action == "ban":
                await member.ban(reason=ar, delete_message_days=1)
                reset_violations(guild_id, member.id)

        except discord.Forbidden:
            pass  # Bot hat nicht genug Berechtigungen
        except Exception as e:
            print(f"  [AUTOMOD] Fehler bei Konsequenz: {e}")

        # ── Log senden ───────────────────────────────────
        log = discord.Embed(
            title     = "🛡️ AutoMod — Verstoß erkannt",
            color     = discord.Color.red() if action in ("ban","kick") else discord.Color.orange(),
            timestamp = datetime.datetime.utcnow()
        )
        log.set_thumbnail(url=member.display_avatar.url)
        log.add_field(name="User",      value=f"{member.mention} (`{member.id}`)", inline=True)
        log.add_field(name="Channel",   value=message.channel.mention,             inline=True)
        log.add_field(name="Grund",     value=reason,                              inline=False)
        log.add_field(name="Verstöße",  value=str(count),                          inline=True)
        if action:
            log.add_field(
                name  = "Konsequenz",
                value = {"warn":"⚠️ Verwarnt","mute":f"🔇 Gemutet ({mute_dur} Min)","kick":"👢 Gekickt","ban":"🔨 Gebannt"}[action],
                inline = True
            )
        log.add_field(name="Nachricht", value=f"```{message.content[:200]}```", inline=False)
        await send_log(message.guild, log)

    # ── Listener ─────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.check_message(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # Nur pruefen wenn Inhalt sich geaendert hat
        if before.content != after.content:
            await self.check_message(after)

    # ── Slash Commands ────────────────────────────────────────

    @app_commands.command(
        name        = "automod",
        description = "AutoMod aktivieren oder deaktivieren"
    )
    @app_commands.describe(status="an = aktivieren, aus = deaktivieren")
    @app_commands.choices(status=[
        app_commands.Choice(name="✅ An",  value="on"),
        app_commands.Choice(name="❌ Aus", value="off"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def automod_toggle(self, interaction: discord.Interaction, status: str):
        cfg = load_data("config.json")
        gid = str(interaction.guild.id)
        if gid not in cfg:
            cfg[gid] = {}
        cfg[gid]["module_automod"] = (status == "on")
        save_data("config.json", cfg)
        state = "✅ aktiviert" if status == "on" else "❌ deaktiviert"
        embed = discord.Embed(
            title       = f"🛡️ AutoMod {state}",
            description = "Schreibe `/setconsequences` um Konsequenzen einzustellen." if status == "on" else "Der AutoMod ist nun inaktiv.",
            color       = discord.Color.green() if status == "on" else discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name        = "addword",
        description = "Fügt ein Wort zur AutoMod-Blacklist hinzu"
    )
    @app_commands.describe(wort="Das verbotene Wort")
    @app_commands.default_permissions(administrator=True)
    async def addword(self, interaction: discord.Interaction, wort: str):
        cfg = load_data("config.json")
        gid = str(interaction.guild.id)
        if gid not in cfg:
            cfg[gid] = {}
        if "badwords" not in cfg[gid]:
            cfg[gid]["badwords"] = []
        wort = wort.lower().strip()
        if wort in cfg[gid]["badwords"]:
            return await interaction.response.send_message(f"❌ `{wort}` ist bereits in der Blacklist!", ephemeral=True)
        cfg[gid]["badwords"].append(wort)
        save_data("config.json", cfg)
        await interaction.response.send_message(f"✅ `{wort}` zur Blacklist hinzugefügt!", ephemeral=True)

    @app_commands.command(
        name        = "removeword",
        description = "Entfernt ein Wort aus der AutoMod-Blacklist"
    )
    @app_commands.describe(wort="Das zu entfernende Wort")
    @app_commands.default_permissions(administrator=True)
    async def removeword(self, interaction: discord.Interaction, wort: str):
        cfg   = load_data("config.json")
        gid   = str(interaction.guild.id)
        wort  = wort.lower().strip()
        words = cfg.get(gid, {}).get("badwords", [])
        if wort not in words:
            return await interaction.response.send_message(f"❌ `{wort}` ist nicht in der Blacklist!", ephemeral=True)
        words.remove(wort)
        cfg[gid]["badwords"] = words
        save_data("config.json", cfg)
        await interaction.response.send_message(f"✅ `{wort}` aus der Blacklist entfernt!", ephemeral=True)

    @app_commands.command(
        name        = "blacklist",
        description = "Zeigt alle verbotenen Wörter der AutoMod-Blacklist"
    )
    @app_commands.default_permissions(administrator=True)
    async def blacklist(self, interaction: discord.Interaction):
        custom = load_data("config.json").get(str(interaction.guild.id), {}).get("badwords", [])
        embed  = discord.Embed(title="🚫 AutoMod Blacklist", color=discord.Color.red())
        embed.add_field(
            name   = f"Standard ({len(DEFAULT_BADWORDS)} Wörter)",
            value  = ", ".join(f"`{w}`" for w in DEFAULT_BADWORDS[:20]),
            inline = False
        )
        embed.add_field(
            name   = f"Eigene ({len(custom)} Wörter)",
            value  = ", ".join(f"`{w}`" for w in custom) if custom else "*Keine eigenen Wörter*",
            inline = False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name        = "setconsequences",
        description = "Stellt ein ab wann AutoMod warnt, mutet, kickt oder bannt"
    )
    @app_commands.describe(
        warn_nach    = "Verstöße bis zur Verwarnung (Standard: 3)",
        mute_nach    = "Verstöße bis zum Mute (Standard: 5)",
        kick_nach    = "Verstöße bis zum Kick (Standard: 8)",
        ban_nach     = "Verstöße bis zum Ban (Standard: 10)",
        mute_dauer   = "Mute-Dauer in Minuten (Standard: 10)"
    )
    @app_commands.default_permissions(administrator=True)
    async def setconsequences(
        self,
        interaction: discord.Interaction,
        warn_nach:  int = 3,
        mute_nach:  int = 5,
        kick_nach:  int = 8,
        ban_nach:   int = 10,
        mute_dauer: int = 10
    ):
        if not (warn_nach < mute_nach < kick_nach < ban_nach):
            return await interaction.response.send_message(
                "❌ Reihenfolge muss sein: Warn < Mute < Kick < Ban!", ephemeral=True
            )
        cfg = load_data("config.json")
        gid = str(interaction.guild.id)
        if gid not in cfg:
            cfg[gid] = {}
        cfg[gid]["automod_consequences"] = {
            "warn_after":    warn_nach,
            "mute_after":    mute_nach,
            "kick_after":    kick_nach,
            "ban_after":     ban_nach,
            "mute_duration": mute_dauer,
        }
        save_data("config.json", cfg)
        embed = discord.Embed(title="✅ Konsequenzen gespeichert", color=discord.Color.green())
        embed.add_field(name="⚠️ Warn",  value=f"ab {warn_nach} Verstößen",                    inline=True)
        embed.add_field(name="🔇 Mute",  value=f"ab {mute_nach} Verstößen ({mute_dauer} Min)", inline=True)
        embed.add_field(name="👢 Kick",  value=f"ab {kick_nach} Verstößen",                    inline=True)
        embed.add_field(name="🔨 Ban",   value=f"ab {ban_nach} Verstößen",                     inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name        = "verstösse",
        description = "Zeigt die AutoMod-Verstöße eines Users"
    )
    @app_commands.describe(user="Der User dessen Verstöße angezeigt werden")
    @app_commands.default_permissions(moderate_members=True)
    async def verstoesse(self, interaction: discord.Interaction, user: discord.Member):
        count = get_violations(interaction.guild.id, user.id)
        cons  = get_consequences(interaction.guild.id)
        embed = discord.Embed(
            title = f"📊 AutoMod-Verstöße: {user.display_name}",
            color = discord.Color.orange()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Verstöße gesamt", value=str(count), inline=True)

        next_a = "✅ Keine weiteren Konsequenzen"
        if   count < cons["warn_after"]: next_a = f"⚠️ Warn bei {cons['warn_after']}"
        elif count < cons["mute_after"]: next_a = f"🔇 Mute bei {cons['mute_after']}"
        elif count < cons["kick_after"]: next_a = f"👢 Kick bei {cons['kick_after']}"
        elif count < cons["ban_after"]:  next_a = f"🔨 Ban bei {cons['ban_after']}"
        embed.add_field(name="Nächste Konsequenz", value=next_a, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name        = "resetverstoesse",
        description = "Setzt die AutoMod-Verstöße eines Users auf 0 zurück"
    )
    @app_commands.describe(user="Der User dessen Verstöße zurückgesetzt werden")
    @app_commands.default_permissions(administrator=True)
    async def resetverstoesse(self, interaction: discord.Interaction, user: discord.Member):
        reset_violations(interaction.guild.id, user.id)
        await interaction.response.send_message(
            f"✅ Verstöße von {user.mention} zurückgesetzt!", ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
