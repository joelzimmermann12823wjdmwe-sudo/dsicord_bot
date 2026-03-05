import os
import functools
from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# --- KONFIGURATION ---
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))

# WICHTIG: Erlaubt zusätzliche Scopes von Discord (behebt deinen Fehler!)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
# Erlaubt HTTP für lokale Tests (Render nutzt HTTPS, daher kein Problem)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

API_BASE_URL = 'https://discord.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- HELPER ---
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_token' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_discord_session(token=None, state=None):
    # Wir fügen 'applications.commands' hinzu, damit es zum Link passt
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
    # Falls der State nicht übereinstimmt, könnte ein Fehler geworfen werden
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
    user = discord.get(API_BASE_URL + '/users/@me').json()
    return jsonify(user)

@app.route('/api/guilds')
@login_required
def get_guilds():
    discord = get_discord_session(token=session['discord_token'])
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    
    # Filtern: Nur Server, auf denen der User Administrator ist
    admin_guilds = []
    if isinstance(guilds, list):
        for g in guilds:
            if (int(g['permissions']) & 0x8) == 0x8:
                g['bot_present'] = True # Hier später echte Prüfung einbauen
                admin_guilds.append(g)
    return jsonify(admin_guilds)

@app.route('/api/guild/<guild_id>/info')
@login_required
def guild_info(guild_id):
    # Dummy-Daten für das Dashboard-Frontend
    data = {
        "channels": [
            {"id": "1", "name": "allgemein"},
            {"id": "2", "name": "logs"}
        ],
        "roles": [
            {"id": "10", "name": "Admin", "color": 16711680},
            {"id": "11", "name": "Moderator", "color": 65280}
        ]
    }
    return jsonify(data)

@app.route('/api/guild/<guild_id>/config', methods=['GET', 'POST'])
@login_required
def guild_config(guild_id):
    if request.method == 'GET':
        # Hier würdest du die Config aus deiner DB laden
        return jsonify({
            "module_logging": True,
            "staff_roles": [],
            "automod": {"filter_badwords": True}
        })
    
    if request.method == 'POST':
        config_data = request.json
        print(f"Speichere Config für {guild_id}: {config_data}")
        return jsonify({"status": "success"})

if __name__ == '__main__':
    # Nutzt den Port von Render oder 5000 lokal
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)