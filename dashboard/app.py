import os
import requests
import functools
from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from requests_oauthlib import OAuth2Session
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Pfad-Fix für Render
base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))
app.secret_key = os.getenv('SECRET_KEY', 'neon_secret_123')

# Config
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# --- AUTH ---
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_token' not in session: return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    discord = OAuth2Session(CLIENT_ID, scope=['identify', 'guilds'], redirect_uri=REDIRECT_URI)
    auth_url, state = discord.authorization_url('https://discord.com/api/oauth2/authorize')
    session['oauth2_state'] = state
    return redirect(auth_url)

@app.route('/callback')
def callback():
    discord = OAuth2Session(CLIENT_ID, state=session.get('oauth2_state'), redirect_uri=REDIRECT_URI)
    token = discord.fetch_token('https://discord.com/api/oauth2/token', client_secret=CLIENT_SECRET, authorization_response=request.url)
    session['discord_token'] = token
    return redirect(url_for('index'))

# --- API ---
@app.route('/api/guilds')
@login_required
def get_guilds():
    discord = OAuth2Session(CLIENT_ID, token=session['discord_token'])
    user_guilds = discord.get('https://discord.com/api/users/@me/guilds').json()
    
    # Bot Präsenz prüfen
    bot_res = requests.get('https://discord.com/api/users/@me/guilds', headers={'Authorization': f'Bot {BOT_TOKEN}'})
    bot_guild_ids = [g['id'] for g in bot_res.json()] if bot_res.ok else []
    
    result = []
    for g in user_guilds:
        if (int(g['permissions']) & 0x8) == 0x8: # Admin check
            g['bot_present'] = g['id'] in bot_guild_ids
            result.append(g)
    return jsonify(result)

@app.route('/api/config/<guild_id>', methods=['GET', 'POST'])
@login_required
def guild_config(guild_id):
    if request.method == 'GET':
        res = supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        return jsonify(res.data[0]['config'] if res.data else {})
    
    if request.method == 'POST':
        data = request.json # Komplette Config vom Frontend
        supabase.table("server_configs").upsert({"guild_id": str(guild_id), "config": data}).execute()
        return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))