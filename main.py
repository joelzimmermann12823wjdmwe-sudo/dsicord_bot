import logging
import os
import time
import webbrowser
from threading import Thread
from urllib.parse import quote_plus

import discord
import requests
from discord import app_commands
from discord.ext import commands
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COGS_DIR = os.path.join(BASE_DIR, "cogs")
HTML_DIR = os.path.join(BASE_DIR, "html")
ENV_PATH = os.path.join(BASE_DIR, ".env")

API_BASE_URL = "https://discord.com/api/v10"
DISCORD_ADMIN_PERMISSION = 0x8
REQUEST_TIMEOUT = 10
DEFAULT_GUILD_SETTINGS = {
    "prefix": "!",
    "welcome_msg": "Willkommen {user}!",
    "welcome_enabled": True,
    "automod_enabled": True,
}


def load_env_file(path: str) -> dict[str, str]:
    env_data: dict[str, str] = {}
    if not os.path.exists(path):
        return env_data

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if "=" not in line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            clean_key = "".join(char for char in key.strip() if char.isalnum() or char == "_")
            env_data[clean_key] = value.strip().strip('"').strip("'")

    return env_data


def parse_bool(value, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def discord_api_request(endpoint: str, token: str, method: str = "GET", **kwargs):
    headers = dict(kwargs.pop("headers", {}))
    headers["Authorization"] = f"Bearer {token}"
    response = requests.request(
        method,
        f"{API_BASE_URL}{endpoint}",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
        **kwargs,
    )
    response.raise_for_status()
    return response.json()


def get_admin_guilds_for_session():
    token = session.get("token")
    if not token:
        return None

    try:
        guilds = discord_api_request("/users/@me/guilds", token)
        if not isinstance(guilds, list):
            raise ValueError("Ungueltige Guild-Antwort")
        return [guild for guild in guilds if int(guild.get("permissions", 0)) & DISCORD_ADMIN_PERMISSION]
    except (requests.RequestException, TypeError, ValueError):
        session.clear()
        return None


def get_authorized_guild(guild_id: int):
    admin_guilds = get_admin_guilds_for_session()
    if admin_guilds is None:
        return None, None

    authorized = next((guild for guild in admin_guilds if int(guild["id"]) == int(guild_id)), None)
    return authorized, admin_guilds


async def send_context_message(ctx, message: str):
    interaction = getattr(ctx, "interaction", None)
    if interaction is not None:
        if not interaction.response.is_done():
            await interaction.response.send_message(message, ephemeral=True)
        else:
            await interaction.followup.send(message, ephemeral=True)
        return

    await ctx.send(message)


env_data = load_env_file(ENV_PATH)

TOKEN = env_data.get("DISCORD_TOKEN")
SUPA_URL = env_data.get("SUPABASE_URL")
SUPA_KEY = env_data.get("SUPABASE_KEY")
OAUTH2_CLIENT_ID = env_data.get("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = env_data.get("OAUTH2_CLIENT_SECRET")
OAUTH2_REDIRECT_URI = env_data.get("OAUTH2_REDIRECT_URI")
FLASK_SECRET_KEY = env_data.get("FLASK_SECRET_KEY", "neon_secret_123")
PORT = int(env_data.get("PORT") or os.environ.get("PORT", "5000"))


class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = None
        self._connect_db()

    def _connect_db(self):
        if not (SUPA_URL and SUPA_KEY):
            return

        try:
            from postgrest import SyncPostgrestClient

            self.db = SyncPostgrestClient(
                f"{SUPA_URL.strip()}/rest/v1",
                headers={
                    "apikey": SUPA_KEY.strip(),
                    "Authorization": f"Bearer {SUPA_KEY.strip()}",
                },
            )
            print("✅ Datenbank-Verbindung aktiv.")
        except Exception as exc:
            print(f"❌ DB-Fehler: {exc}")

    def is_target_banned(self, target_id: int | str, ban_type: str) -> bool:
        if not self.db:
            return False

        try:
            res = (
                self.db.table("bot_bans")
                .select("target_id")
                .eq("target_id", str(target_id))
                .eq("type", ban_type)
                .execute()
            )
            return bool(res.data)
        except Exception:
            return False

    async def interaction_ban_check(self, interaction: discord.Interaction) -> bool:
        if not self.db:
            return True

        if self.is_target_banned(interaction.user.id, "user"):
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "🚫 Du bist von der Nutzung dieses Bots ausgeschlossen.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "🚫 Du bist von der Nutzung dieses Bots ausgeschlossen.",
                    ephemeral=True,
                )
            return False

        if interaction.guild and self.is_target_banned(interaction.guild.id, "guild"):
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "🚫 Dieser Server wurde von der Bot-Nutzung ausgeschlossen.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    "🚫 Dieser Server wurde von der Bot-Nutzung ausgeschlossen.",
                    ephemeral=True,
                )
            await interaction.guild.leave()
            return False

        return True

    async def setup_hook(self):
        self.tree.interaction_check = self.interaction_ban_check
        self.tree.on_error = self.on_tree_error

        if os.path.isdir(COGS_DIR):
            for filename in sorted(os.listdir(COGS_DIR)):
                if not filename.endswith(".py") or filename.startswith("__"):
                    continue

                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ Cog geladen: {filename[:-3]}")
                except Exception as exc:
                    print(f"❌ Fehler beim Laden von {filename}: {exc}")

        try:
            synced = await self.tree.sync()
            print(f"⚡ Slash-Commands synchronisiert: {len(synced)} Befehle")
        except Exception as exc:
            print(f"❌ Fehler beim Sync: {exc}")

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            return
        print(f"⚠️ Slash-Error: {error}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            return
        print(f"⚠️ Prefix-Error: {error}")


bot = NeonBot()

app = Flask(__name__, template_folder=HTML_DIR)
app.secret_key = FLASK_SECRET_KEY
logging.getLogger("werkzeug").setLevel(logging.ERROR)


@bot.event
async def on_ready():
    print(f"🤖 Bot eingeloggt als {bot.user.name}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="!help | Neon Bot")
    )


@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    prefix = "!"
    if bot.db:
        try:
            res = (
                bot.db.table("guild_settings")
                .select("prefix")
                .eq("guild_id", str(message.guild.id))
                .execute()
            )
            if res.data:
                prefix = res.data[0].get("prefix") or "!"
        except Exception:
            pass

    if message.content.startswith(prefix):
        await bot.process_commands(message)


@app.route("/")
def home():
    if "user" in session and session.get("token"):
        return redirect(url_for("dashboard"))

    oauth_ready = all((OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, OAUTH2_REDIRECT_URI))
    return render_template("index.html", oauth_ready=oauth_ready)


@app.route("/login")
def login():
    if not all((OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, OAUTH2_REDIRECT_URI)):
        return "OAuth-Konfiguration unvollstaendig.", 503

    encoded_redirect_uri = quote_plus(OAUTH2_REDIRECT_URI)
    url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={OAUTH2_CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={encoded_redirect_uri}"
        "&scope=identify+guilds"
    )
    return redirect(url)


@app.route("/callback")
def callback():
    if not all((OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, OAUTH2_REDIRECT_URI)):
        return "OAuth-Konfiguration unvollstaendig.", 503

    code = request.args.get("code")
    if not code:
        return "Login fehlgeschlagen: Kein OAuth-Code uebergeben.", 400

    try:
        token_response = requests.post(
            f"{API_BASE_URL}/oauth2/token",
            data={
                "client_id": OAUTH2_CLIENT_ID,
                "client_secret": OAUTH2_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": OAUTH2_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=REQUEST_TIMEOUT,
        )
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")
        if not access_token:
            return "Login fehlgeschlagen.", 400

        user_data = discord_api_request("/users/@me", access_token)
    except requests.RequestException:
        return "Login fehlgeschlagen.", 400

    session["user"] = user_data
    session["token"] = access_token
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    admin_guilds = get_admin_guilds_for_session()
    if admin_guilds is None:
        return redirect(url_for("home"))

    for guild in admin_guilds:
        guild["bot_in"] = bot.get_guild(int(guild["id"])) is not None

    return render_template("dashboard.html", user=session["user"], guilds=admin_guilds)


@app.route("/server/<int:guild_id>")
def server_page(guild_id):
    if "user" not in session:
        return redirect(url_for("home"))

    authorized_guild, admin_guilds = get_authorized_guild(guild_id)
    if admin_guilds is None:
        return redirect(url_for("home"))
    if authorized_guild is None:
        return "Keine Berechtigung fuer diesen Server.", 403

    guild = bot.get_guild(guild_id)
    if not guild:
        return "Bot nicht auf diesem Server.", 404

    settings = dict(DEFAULT_GUILD_SETTINGS)
    if bot.db:
        try:
            res = bot.db.table("guild_settings").select("*").eq("guild_id", str(guild_id)).execute()
            if res.data:
                settings.update(res.data[0])
        except Exception:
            pass

    return render_template("server.html", guild=guild, user=session["user"], settings=settings)


@app.route("/api/save-settings", methods=["POST"])
def api_save_settings():
    if "user" not in session:
        return jsonify({"success": False, "error": "Nicht eingeloggt."}), 401

    data = request.get_json(silent=True) or {}
    guild_id = data.get("guild_id")
    if not guild_id:
        return jsonify({"success": False, "error": "Keine Guild ID angegeben."}), 400

    try:
        guild_id_int = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Ungueltige Guild ID."}), 400

    authorized_guild, admin_guilds = get_authorized_guild(guild_id_int)
    if admin_guilds is None:
        return jsonify({"success": False, "error": "Sitzung abgelaufen."}), 401
    if authorized_guild is None:
        return jsonify({"success": False, "error": "Keine Berechtigung fuer diesen Server."}), 403
    if not bot.db:
        return jsonify({"success": False, "error": "Datenbank nicht verfuegbar."}), 500

    payload = {
        "guild_id": str(guild_id_int),
        "prefix": str(data.get("prefix") or "!").strip()[:10] or "!",
        "welcome_msg": str(data.get("welcome_msg") or DEFAULT_GUILD_SETTINGS["welcome_msg"]).strip(),
        "welcome_enabled": parse_bool(data.get("welcome_enabled"), True),
        "automod_enabled": parse_bool(data.get("automod_enabled"), True),
    }

    try:
        bot.db.table("guild_settings").upsert(payload).execute()
        return jsonify({"success": True})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/save-tickets", methods=["POST"])
def save_tickets():
    if "user" not in session:
        return jsonify({"success": False, "error": "Nicht eingeloggt."}), 401

    data = request.get_json(silent=True) or {}
    guild_id = data.get("guild_id")
    panels = data.get("panels", [])

    if not guild_id:
        return jsonify({"success": False, "error": "Keine Guild ID angegeben."}), 400
    if not isinstance(panels, list):
        return jsonify({"success": False, "error": "Ungueltige Ticket-Daten."}), 400

    try:
        guild_id_int = int(guild_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Ungueltige Guild ID."}), 400

    authorized_guild, admin_guilds = get_authorized_guild(guild_id_int)
    if admin_guilds is None:
        return jsonify({"success": False, "error": "Sitzung abgelaufen."}), 401
    if authorized_guild is None:
        return jsonify({"success": False, "error": "Keine Berechtigung fuer diesen Server."}), 403
    if not bot.db:
        return jsonify({"success": False, "error": "Datenbank nicht verfuegbar."}), 500

    try:
        bot.db.table("ticket_panels").delete().eq("guild_id", str(guild_id_int)).execute()

        for panel in panels[:3]:
            if not isinstance(panel, dict):
                continue

            bot.db.table("ticket_panels").insert(
                {
                    "guild_id": str(guild_id_int),
                    "panel_name": panel.get("panel_name"),
                    "support_role_id": panel.get("support_role_id"),
                    "channel_id": panel.get("channel_id"),
                    "category_id": panel.get("category_id"),
                    "ticket_categories": panel.get("ticket_categories") or [],
                }
            ).execute()

        return jsonify({"success": True})
    except Exception as exc:
        print(f"Fehler beim Ticket-Speichern: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@bot.check
async def global_ban_check(ctx):
    if not bot.db:
        return True

    if bot.is_target_banned(ctx.author.id, "user"):
        await send_context_message(ctx, "🚫 Du bist von der Nutzung dieses Bots ausgeschlossen.")
        return False

    if ctx.guild and bot.is_target_banned(ctx.guild.id, "guild"):
        await send_context_message(ctx, "🚫 Dieser Server wurde von der Bot-Nutzung ausgeschlossen.")
        await ctx.guild.leave()
        return False

    return True


@bot.event
async def on_guild_join(guild):
    if not bot.db:
        return

    if bot.is_target_banned(guild.id, "guild"):
        print(f"🚫 Gebannten Server {guild.name} beigetreten. Verlasse sofort...")
        await guild.leave()


def run_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def open_dashboard_in_browser():
    dashboard_url = f"http://127.0.0.1:{PORT}"

    for _ in range(30):
        try:
            response = requests.get(dashboard_url, timeout=1, allow_redirects=False)
            if response.status_code < 500:
                webbrowser.open(dashboard_url, new=2)
                return
        except requests.RequestException:
            pass

        time.sleep(0.5)


if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN fehlt in der .env.")
    else:
        Thread(target=run_flask, daemon=True).start()
        Thread(target=open_dashboard_in_browser, daemon=True).start()
        bot.run(TOKEN)
