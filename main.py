import discord
from discord.ext import commands
from discord import app_commands
import os
import requests
import warnings
from flask import Flask, render_template, redirect, session, url_for, request
from threading import Thread

# Unterdrückt Warnungen
warnings.filterwarnings("ignore", category=DeprecationWarning) 

from postgrest import SyncPostgrestClient
from gotrue import SyncGoTrueClient

# --- .ENV MANUELL EINLESEN ---
env_vars = {}
try:
    with open(".env", "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
except Exception as e:
    print(f"❌ Fehler beim Lesen der .env: {e}")

TOKEN = env_vars.get("DISCORD_TOKEN")
SUPA_URL = env_vars.get("SUPABASE_URL")
SUPA_KEY = env_vars.get("SUPABASE_KEY")
CLIENT_ID = env_vars.get("DISCORD_CLIENT_ID")
CLIENT_SECRET = env_vars.get("DISCORD_CLIENT_SECRET")
REDIRECT_URI = env_vars.get("DISCORD_REDIRECT_URI")

# --- FLASK DASHBOARD ---
base_dir = os.path.dirname(os.path.abspath(__file__))
html_dir = os.path.join(base_dir, 'html')
app = Flask(__name__, template_folder=html_dir)
app.secret_key = env_vars.get("FLASK_SECRET_KEY", "neon_secret_888")

@app.route('/')
def home():
    return render_template('home.html', user=session.get('user'))

@app.route('/login')
def login():
    auth_url = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&response_type=code&redirect_uri={REDIRECT_URI}&scope=identify+guilds"
    return redirect(auth_url)

# ... (Rest der Flask-Routen bleibt gleich) ...

# --- NEON BOT MIT SLASH COMMAND FOKUS ---
class NeonBot(commands.Bot):
    def __init__(self):
        # Intents für den Bot
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # Datenbank Verbindung
        if SUPA_URL and SUPA_KEY:
            self.db = SyncPostgrestClient(f"{SUPA_URL}/rest/v1", headers={
                "apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"
            })

    async def setup_hook(self):
        # Cogs laden und Bestätigung ausgeben
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"Geladen: {filename}")

        # Globales Synchronisieren der Slash-Commands
        # Das sorgt dafür, dass die Commands überall verfügbar sind (keine Duplikate)
        await self.tree.sync()
        print("✅ Alle Slash-Commands wurden global synchronisiert.")

    async def on_ready(self):
        print(f'⚡ {self.user.name} ist jetzt online!')

bot = NeonBot()

# --- START ---
if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=10000, use_reloader=False), daemon=True).start()
    bot.run(TOKEN)