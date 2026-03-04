import os
from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import functools

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Sicherheits-Check: Wenn eine Variable fehlt, stoppe sofort mit Fehlermeldung
if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    print("❌ FEHLER: CLIENT_ID, CLIENT_SECRET oder REDIRECT_URI fehlt in der .env!")
    
API_BASE_URL = 'https://discord.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24)) # Nutzt SECRET_KEY aus .env oder generiert einen

# Erlaubt HTTP für lokale Tests
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# --- HELPER: LOGIN CHECK ---
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_token' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_discord_session(token=None, state=None):
    return OAuth2Session(CLIENT_ID, 
                         token=token, 
                         state=state, 
                         scope=['identify', 'guilds'], 
                         redirect_uri=REDIRECT_URI)

# --- ROUTES ---

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
    discord = get_discord_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)
    session['discord_token'] = token
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- API ENDPUNKTE ---

@app.route('/api/me')
@login_required
def get_me():
    try:
        discord = get_discord_session(token=session['discord_token'])
        user = discord.get(API_BASE_URL + '/users/@me').json()
        return jsonify(user)
    except:
        return jsonify({"error": "Failed to fetch user"}), 400

@app.route('/api/guilds')
@login_required
def get_guilds():
    discord = get_discord_session(token=session['discord_token'])
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    
    admin_guilds = []
    for g in guilds:
        # Permission Check: Administrator (0x8)
        if (int(g['permissions']) & 0x8) == 0x8:
            # Hier später die Prüfung einbauen, ob der Bot wirklich auf dem Server ist
            g['bot_present'] = True 
            admin_guilds.append(g)
            
    return jsonify(admin_guilds)

@app.route('/api/guild/<guild_id>/info')
@login_required
def guild_info(guild_id):
    # Dummy-Daten für die UI-Vorschau
    data = {
        "channels": [{"id": "1", "name": "allgemein"}, {"id": "2", "name": "logs"}],
        "roles": [{"id": "10", "name": "Admin", "color": 16711680}, {"id": "11", "name": "Mod", "color": 65280}],
        "categories": [{"id": "100", "name": "SUPPORT"}]
    }
    return jsonify(data)

@app.route('/api/guild/<guild_id>/config', methods=['GET', 'POST'])
@login_required
def guild_config(guild_id):
    if request.method == 'GET':
        # Hier später Datenbank-Abfrage einbauen
        return jsonify({"module_logging": True, "automod": {"filter_badwords": True}})
    
    if request.method == 'POST':
        data = request.json
        print(f"DEBUG: Speichere {data} für Server {guild_id}")
        return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Port 5000 für lokale Entwicklung
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))