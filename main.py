import discord
from discord.ext import commands
from discord import app_commands
import os
import requests
import warnings
from flask import Flask, render_template, redirect, session, url_for, request
from threading import Thread
from dotenv import load_dotenv
from urllib.parse import urlencode

# Unterdrückt veraltete Warnungen
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Falls du diese Pakete für Supabase nutzt:
try:
    from postgrest import SyncPostgrestClient
except ImportError:
    SyncPostgrestClient = None

# --- KONFIGURATION LADEN ---
# load_dotenv sucht nach einer .env Datei. Wenn keine da ist (wie auf Render), 
# wird dieser Schritt einfach übersprungen, ohne einen Fehler zu werfen.
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_KEY")
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI") # Auf Render in Env setzen!

# --- FLASK DASHBOARD ---
base_dir = os.path.dirname(os.path.abspath(__file__))
html_dir = os.path.join(base_dir, 'html')

app = Flask(__name__, template_folder=html_dir)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "neon_secret_888")

@app.route('/')
def home():
    # Wir nutzen 'home.html' wie in deinem Ordner gesehen
    return render_template('home.html', user=session.get('user'))

@app.route('/login')
def login():
    # Wir bauen die Parameter sauber als Dictionary auf
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify guilds',
        'permissions': '8'
    }
    
    # urlencode macht aus dem Dictionary einen perfekt formatierten String
    auth_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    
    print(f"DEBUG: Redirect URI ist: {REDIRECT_URI}") # Das sehen wir dann in den Render Logs
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for('home'))
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    r = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers).json()
    access_token = r.get('access_token')
    
    if access_token:
        user_data = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f"Bearer {access_token}"}).json()
        session['user'] = user_data
        return redirect(url_for('wartung'))
    
    return redirect(url_for('home'))

@app.route('/wartung')
def wartung():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('wartung.html', user=session['user'])

# --- NEON BOT KLASSE ---
class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # Datenbank-Client initialisieren
        if SUPA_URL and SUPA_KEY and SyncPostgrestClient:
            self.db = SyncPostgrestClient(f"{SUPA_URL}/rest/v1", headers={
                "apikey": SUPA_KEY, "Authorization": f"Bearer {SUPA_KEY}"
            })
            print("✅ Datenbank-Verbindung konfiguriert.")

    async def setup_hook(self):
        # Cogs automatisch laden
        cogs_path = os.path.join(base_dir, 'cogs')
        if os.path.exists(cogs_path):
            for filename in os.listdir(cogs_path):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"Geladen: {filename}")
                    except Exception as e:
                        print(f"❌ Fehler beim Laden von {filename}: {e}")

        # Slash Commands global synchronisieren
        await self.tree.sync()
        print("✅ Slash-Commands global synchronisiert.")

    async def on_ready(self):
        print(f'⚡ {self.user.name} ist online und bereit!')

bot = NeonBot()

# --- START FUNKTION ---
def run_flask():
    # Port 10000 ist Standard für Render
    app.run(host='0.0.0.0', port=10000, use_reloader=False)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ FEHLER: Kein DISCORD_TOKEN gefunden. Bot kann nicht starten.")
    else:
        # Flask in einem eigenen Thread starten
        Thread(target=run_flask, daemon=True).start()
        # Bot starten
        bot.run(TOKEN)