import discord, datetime, re
from datetime import timedelta
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data, is_module_enabled, get_log_channel_id

DEFAULT_BADWORDS = [
    "hurensohn","wichser","scheiße","scheisse","arschloch",
    "vollidiot","blödmann","blodmann","fick","ficker",
    "fotze","nutte","bastard","schlampe","dummkopf",
    "trottel","depp","missgeburt","hurenkind",
]


def get_badwords(gid: int) -> list:
    custom = load_data("config.json").get(str(gid), {}).get("badwords", [])
    return list(set(DEFAULT_BADWORDS + [w.lower().strip() for w in custom]))


def get_consequences(gid: int) -> dict:
    d = {"warn_after":3,"mute_after":5,"kick_after":8,"ban_after":10,"mute_duration":10}
    d.update(load_data("config.json").get(str(gid), {}).get("automod_consequences", {}))
    return d


def add_violation(gid: int, uid: int) -> int:
    v = load_data("automod_violations.json")
    g, u = str(gid), str(uid)
    if g not in v: v[g] = {}
    v[g][u] = int(v[g].get(u, 0)) + 1
    save_data("automod_violations.json", v)
    return v[g][u]


def get_violations(gid: int, uid: int) -> int:
    return int(load_data("automod_violations.json").get(str(gid), {}).get(str(uid), 0))


def reset_violations(gid: int, uid: int):
    v = load_data("automod_violations.json")
    g, u = str(gid), str(uid)
    if g in v: v[g][u] = 0
    save_data("automod_violations.json", v)


async def try_dm(user, embed):
    try: await user.send(embed=embed)
    except: pass


async def post_log(guild, embed):
    ch_id = get_log_channel_id(guild.id)
    if not ch_id: return
    ch = guild.get_channel(int(ch_id))
    if ch:
        try: await ch.send(embed=embed)
        except: pass


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_message(self, message: discord.Message):
        if not message.guild or message.author.bot or not message.content:
            return
        if not is_module_enabled(message.guild.id, "automod"):
            return
        p = message.author.guild_permissions
        if p.administrator or p.manage_messages or p.manage_guild:
            return

        content   = message.content.lower()
        gid       = message.guild.id
        triggered = False
        reason    = None

        for word in get_badwords(gid):
            if word in content:
                triggered, reason = True, f"Verbotenes Wort: `{word}`"
                break

        if not triggered:
            if re.search(r"discord\.(gg|com/invite)/[a-zA-Z0-9\-]+", content):
                triggered, reason = True, "Discord Invite-Link"

        if not triggered and len(message.mentions) > 5:
            triggered, reason = True, f"Massen-Ping ({len(message.mentions)} User)"

        if not triggered and len(content) > 15:
            letters = [c for c in content if c.isalpha()]
            if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.75:
                triggered, reason = True, "Caps-Spam"

        if not triggered:
            return

        try:
            await message.delete()
        except (discord.NotFound, discord.Forbidden):
            return

        count = add_violation(gid, message.author.id)
        cons  = get_consequences(gid)
        wa, ma, ka, ba, md = cons["warn_after"], cons["mute_after"], cons["kick_after"], cons["ban_after"], cons["mute_duration"]

        action = None
        if   count >= ba: action = "ban"
        elif count >= ka: action = "kick"
        elif count >= ma: action = "mute"
        elif count >= wa: action = "warn"

        color = discord.Color.red() if action in ("ban","kick") else discord.Color.orange()
        dm    = discord.Embed(title=f"⚠️ AutoMod — {message.guild.name}", color=color, timestamp=datetime.datetime.utcnow())
        dm.add_field(name="Grund",     value=reason,                    inline=False)
        dm.add_field(name="Verstösse", value=str(count),                inline=True)
        dm.add_field(name="Channel",   value=message.channel.mention,   inline=True)
        texts = {
            "warn": f"⚠️ Verwarnung! ({count}/{wa})",
            "mute": f"🔇 Gemutet {md} Min! ({count}/{ma})",
            "kick": f"👢 Gekickt! ({count}/{ka})",
            "ban":  f"🔨 Gebannt! ({count}/{ba})",
        }
        if action:
            dm.add_field(name="Konsequenz", value=texts[action], inline=False)
        else:
            dm.add_field(name="Hinweis", value=f"Noch {wa - count} Verstoss/Verstoesse bis Verwarnung.", inline=False)
        dm.set_footer(text="Neon Bot • AutoMod")
        await try_dm(message.author, dm)

        ar = f"AutoMod: {reason} ({count} Verstoesse)"
        try:
            if action == "warn":
                w = load_data("warnings.json")
                uid = str(message.author.id)
                if uid not in w: w[uid] = []
                w[uid].append({"reason": f"AutoMod: {reason}", "mod": "AutoMod", "time": datetime.datetime.utcnow().isoformat()})
                save_data("warnings.json", w)
            elif action == "mute":
                await message.author.timeout(timedelta(minutes=md), reason=ar)
            elif action == "kick":
                await message.author.kick(reason=ar)
                reset_violations(gid, message.author.id)
            elif action == "ban":
                await message.author.ban(reason=ar, delete_message_days=1)
                reset_violations(gid, message.author.id)
        except discord.Forbidden:
            pass
        except Exception as e:
            print(f"  [AUTOMOD] Fehler: {e}")

        log = discord.Embed(title="🛡️ AutoMod — Verstoss", color=color, timestamp=datetime.datetime.utcnow())
        log.set_thumbnail(url=message.author.display_avatar.url)
        log.add_field(name="User",      value=f"{message.author.mention} (`{message.author.id}`)", inline=True)
        log.add_field(name="Channel",   value=message.channel.mention,                             inline=True)
        log.add_field(name="Grund",     value=reason,                                              inline=False)
        log.add_field(name="Verstoesse", value=str(count),                                         inline=True)
        if action:
            log.add_field(name="Konsequenz", value={"warn":"⚠️ Verwarnt","mute":f"🔇 Gemutet ({md} Min)","kick":"👢 Gekickt","ban":"🔨 Gebannt"}[action], inline=True)
        log.add_field(name="Nachricht", value=f"```{message.content[:200]}```", inline=False)
        await post_log(message.guild, log)

    @commands.Cog.listener()
    async def on_message(self, message): await self.check_message(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content: await self.check_message(after)

    @app_commands.command(name="automod", description="AutoMod aktivieren oder deaktivieren")
    @app_commands.describe(status="an = aktivieren | aus = deaktivieren")
    @app_commands.choices(status=[app_commands.Choice(name="✅ An", value="on"), app_commands.Choice(name="❌ Aus", value="off")])
    @app_commands.default_permissions(administrator=True)
    async def automod_toggle(self, interaction: discord.Interaction, status: str):
        cfg = load_data("config.json"); gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["module_automod"] = (status == "on"); save_data("config.json", cfg)
        aktiv = status == "on"
        e = discord.Embed(title=f"🛡️ AutoMod {'aktiviert ✅' if aktiv else 'deaktiviert ❌'}", color=discord.Color.green() if aktiv else discord.Color.red())
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="addword", description="Fuegt ein Wort zur AutoMod-Blacklist hinzu")
    @app_commands.describe(wort="Das verbotene Wort")
    @app_commands.default_permissions(administrator=True)
    async def addword(self, interaction: discord.Interaction, wort: str):
        cfg = load_data("config.json"); gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        if "badwords" not in cfg[gid]: cfg[gid]["badwords"] = []
        wort = wort.lower().strip()
        if wort in cfg[gid]["badwords"]:
            return await interaction.response.send_message(f"❌ `{wort}` ist bereits in der Blacklist!", ephemeral=True)
        cfg[gid]["badwords"].append(wort); save_data("config.json", cfg)
        await interaction.response.send_message(f"✅ `{wort}` hinzugefuegt!", ephemeral=True)

    @app_commands.command(name="removeword", description="Entfernt ein Wort aus der AutoMod-Blacklist")
    @app_commands.describe(wort="Das zu entfernende Wort")
    @app_commands.default_permissions(administrator=True)
    async def removeword(self, interaction: discord.Interaction, wort: str):
        cfg = load_data("config.json"); gid = str(interaction.guild.id)
        wort = wort.lower().strip()
        words = cfg.get(gid, {}).get("badwords", [])
        if wort not in words:
            return await interaction.response.send_message(f"❌ `{wort}` nicht in der Blacklist!", ephemeral=True)
        words.remove(wort)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["badwords"] = words; save_data("config.json", cfg)
        await interaction.response.send_message(f"✅ `{wort}` entfernt!", ephemeral=True)

    @app_commands.command(name="blacklist", description="Zeigt alle verbotenen Woerter der Blacklist")
    @app_commands.default_permissions(administrator=True)
    async def blacklist(self, interaction: discord.Interaction):
        custom = load_data("config.json").get(str(interaction.guild.id), {}).get("badwords", [])
        e = discord.Embed(title="🚫 AutoMod Blacklist", color=discord.Color.red())
        e.add_field(name=f"Standard ({len(DEFAULT_BADWORDS)})", value=", ".join(f"`{w}`" for w in DEFAULT_BADWORDS), inline=False)
        e.add_field(name=f"Eigene ({len(custom)})", value=", ".join(f"`{w}`" for w in custom) if custom else "*Keine*", inline=False)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="setconsequences", description="Stellt ein ab wann AutoMod verwarnt, mutet, kickt oder bannt")
    @app_commands.describe(warn_nach="Verstoesse bis Warn (Std: 3)", mute_nach="Verstoesse bis Mute (Std: 5)", kick_nach="Verstoesse bis Kick (Std: 8)", ban_nach="Verstoesse bis Ban (Std: 10)", mute_dauer="Mute-Dauer Minuten (Std: 10)")
    @app_commands.default_permissions(administrator=True)
    async def setconsequences(self, interaction: discord.Interaction, warn_nach: int = 3, mute_nach: int = 5, kick_nach: int = 8, ban_nach: int = 10, mute_dauer: int = 10):
        if not (warn_nach < mute_nach < kick_nach < ban_nach):
            return await interaction.response.send_message("❌ Reihenfolge: Warn < Mute < Kick < Ban!", ephemeral=True)
        cfg = load_data("config.json"); gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["automod_consequences"] = {"warn_after":warn_nach,"mute_after":mute_nach,"kick_after":kick_nach,"ban_after":ban_nach,"mute_duration":mute_dauer}
        save_data("config.json", cfg)
        e = discord.Embed(title="✅ Konsequenzen gespeichert", color=discord.Color.green())
        e.add_field(name="⚠️ Warn", value=f"ab {warn_nach}", inline=True)
        e.add_field(name="🔇 Mute", value=f"ab {mute_nach} ({mute_dauer} Min)", inline=True)
        e.add_field(name="👢 Kick", value=f"ab {kick_nach}", inline=True)
        e.add_field(name="🔨 Ban",  value=f"ab {ban_nach}",  inline=True)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="verstoesse", description="Zeigt die AutoMod-Verstoesse eines Users")
    @app_commands.describe(user="Der User")
    @app_commands.default_permissions(moderate_members=True)
    async def verstoesse(self, interaction: discord.Interaction, user: discord.Member):
        count = get_violations(interaction.guild.id, user.id)
        cons  = get_consequences(interaction.guild.id)
        e = discord.Embed(title=f"📊 Verstoesse: {user.display_name}", color=discord.Color.orange())
        e.set_thumbnail(url=user.display_avatar.url)
        e.add_field(name="Verstoesse", value=str(count), inline=True)
        next_a = "✅ Keine"
        if   count < cons["warn_after"]: next_a = f"⚠️ Warn bei {cons['warn_after']}"
        elif count < cons["mute_after"]: next_a = f"🔇 Mute bei {cons['mute_after']}"
        elif count < cons["kick_after"]: next_a = f"👢 Kick bei {cons['kick_after']}"
        elif count < cons["ban_after"]:  next_a = f"🔨 Ban bei {cons['ban_after']}"
        e.add_field(name="Naechste Konsequenz", value=next_a, inline=True)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="resetverstoesse", description="Setzt Verstoesse eines Users auf 0 zurueck")
    @app_commands.describe(user="Der User")
    @app_commands.default_permissions(administrator=True)
    async def resetverstoesse(self, interaction: discord.Interaction, user: discord.Member):
        reset_violations(interaction.guild.id, user.id)
        await interaction.response.send_message(f"✅ Verstoesse von {user.mention} zurueckgesetzt!", ephemeral=True)


async def setup(bot): await bot.add_cog(AutoMod(bot))
