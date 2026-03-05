import os
import json
import functools
import requests
from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from requests_oauthlib import OAuth2Session
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Umgebung laden
load_dotenv()

# Pfad-Konfiguration für Flask (wichtig für Render!)
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

# 2. API Keys & OAuth Setup
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
BOT_TOKEN = os.getenv('DISCORD_TOKEN')

# Supabase Initialisierung
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# WICHTIG: OAuth Fixes
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

API_BASE_URL = 'https://discord.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

# --- HELPER ---
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_discord_session(token=None, state=None):
    # Scopes passend zum Einladungslink
    scope = ['identify', 'guilds', 'applications.commands']
    return OAuth2Session(
        CLIENT_ID, 
        token=token, 
        state=state, 
        scope=scope, 
        redirect_uri=REDIRECT_URI
    )

# --- WEB ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    discord = get_discord_session()
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    try:
        discord = get_discord_session(state=session.get('oauth2_state'))
        token = discord.fetch_token(
            TOKEN_URL, 
            client_secret=CLIENT_SECRET, 
            authorization_response=request.url
        )
        session['discord_token'] = token
        return redirect(url_for('index'))
    except Exception as e:
        return f"Login fehlgeschlagen: {str(e)}", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- API ENDPUNKTE ---

@app.route('/api/me')
@login_required
def get_me():
    discord = get_discord_session(token=session['discord_token'])
    user = discord.get(API_BASE_URL + '/users/@me').json()
    return jsonify(user)

@app.route('/api/guilds')
@login_required
def get_guilds():
    discord = get_discord_session(token=session['discord_token'])
    user_guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    
    # Check auf welchen Servern der BOT ist
    bot_headers = {'Authorization': f'Bot {BOT_TOKEN}'}
    bot_res = requests.get(f'{API_BASE_URL}/users/@me/guilds', headers=bot_headers)
    bot_guild_ids = [g['id'] for g in bot_res.json()] if bot_res.ok else []
    
    admin_guilds = []
    if isinstance(user_guilds, list):
        for g in user_guilds:
            # Permissions Check (Administrator Bit = 0x8)
            if (int(g['permissions']) & 0x8) == 0x8:
                # Markierung ob der Bot da ist (für rote/grüne Anzeige)
                g['bot_present'] = g['id'] in bot_guild_ids
                admin_guilds.append(g)
    return jsonify(admin_guilds)

@app.route('/api/guild/<guild_id>/config', methods=['GET', 'POST'])
@login_required
def guild_config(guild_id):
    if request.method == 'GET':
        # Daten aus Supabase laden
        res = supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        if res.data:
            return jsonify(res.data[0]['config'])
        return jsonify({}) # Leere Config wenn neu

    if request.method == 'POST':
        req_data = request.json # Erwartet { "module": "automod", "config": {...} }
        module = req_data.get('module')
        module_config = req_data.get('config')

        # Aktuelle Gesamt-Config holen
        res = supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        full_config = res.data[0]['config'] if res.data else {}
        
        # Modul-Teil aktualisieren
        full_config[module] = module_config

        # Zurück in Supabase speichern (Upsert)
        supabase.table("server_configs").upsert({
            "guild_id": str(guild_id), 
            "config": full_config
        }).execute()
        
        return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)