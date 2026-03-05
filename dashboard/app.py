import os
import functools
import json
import requests
from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
BOT_TOKEN = os.getenv('DISCORD_TOKEN') # Der Token deines Bots aus der .env
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

API_BASE_URL = 'https://discord.com/api'
app = Flask(__name__)
app.secret_key = SECRET_KEY
CONFIG_FILE = 'server_configs.json' # Hier speichert das Dashboard alles!

# --- HELPER FUNKTIONEN ---
def load_configs():
    if not os.path.exists(CONFIG_FILE): return {}
    with open(CONFIG_FILE, 'r') as f: return json.load(f)

def save_configs(data):
    with open(CONFIG_FILE, 'w') as f: json.dump(data, f, indent=4)

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_token' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_discord_session(token=None, state=None):
    return OAuth2Session(CLIENT_ID, token=token, state=state, scope=['identify', 'guilds', 'applications.commands'], redirect_uri=REDIRECT_URI)

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    discord = get_discord_session()
    auth_url, state = discord.authorization_url(API_BASE_URL + '/oauth2/authorize')
    session['oauth2_state'] = state
    return redirect(auth_url)

@app.route('/callback')
def callback():
    try:
        discord = get_discord_session(state=session.get('oauth2_state'))
        token = discord.fetch_token(API_BASE_URL + '/oauth2/token', client_secret=CLIENT_SECRET, authorization_response=request.url)
        session['discord_token'] = token
        return redirect(url_for('index'))
    except Exception as e:
        return f"Fehler beim Login: {str(e)}", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- API ENDPUNKTE ---
@app.route('/api/me')
@login_required
def get_me():
    discord = get_discord_session(token=session['discord_token'])
    return jsonify(discord.get(API_BASE_URL + '/users/@me').json())

@app.route('/api/guilds')
@login_required
def get_guilds():
    discord = get_discord_session(token=session['discord_token'])
    user_guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    
    # Hole die Server, auf denen der BOT ist
    bot_headers = {'Authorization': f'Bot {BOT_TOKEN}'}
    bot_req = requests.get(f'{API_BASE_URL}/users/@me/guilds', headers=bot_headers)
    bot_guild_ids = [g['id'] for g in bot_req.json()] if bot_req.ok else []
    
    admin_guilds = []
    if isinstance(user_guilds, list):
        for g in user_guilds:
            if (int(g['permissions']) & 0x8) == 0x8: # Ist der User Admin?
                # ECHTER CHECK: Ist der Bot auf diesem Server?
                g['bot_present'] = g['id'] in bot_guild_ids
                admin_guilds.append(g)
    return jsonify(admin_guilds)

@app.route('/api/guild/<guild_id>/info')
@login_required
def guild_info(guild_id):
    # Später können wir hier echte Rollen/Kanäle vom Bot laden
    return jsonify({"channels": [], "roles": [], "categories": []})

@app.route('/api/guild/<guild_id>/config', methods=['GET', 'POST'])
@login_required
def guild_config(guild_id):
    configs = load_configs()
    guild_data = configs.get(str(guild_id), {})

    if request.method == 'GET':
        return jsonify(guild_data)
    
    if request.method == 'POST':
        req_data = request.json
        module = req_data.get('module')
        
        if str(guild_id) not in configs:
            configs[str(guild_id)] = {}
            
        configs[str(guild_id)][module] = req_data.get('config')
        save_configs(configs)
        return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)