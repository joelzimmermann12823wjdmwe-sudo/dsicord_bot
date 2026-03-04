import json, os, requests
from pathlib import Path
from flask import Flask, redirect, request, session, jsonify, render_template
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SECRET", "neon-secret-key-2025")

CLIENT_ID     = "1470766309192241224"
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI  = "http://localhost:5000/callback"
DATA_FILE     = ROOT / "data" / "guild_configs.json"

def _load():
    if not DATA_FILE.exists(): return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def _save(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4)

@app.route("/")
def index(): return render_template("index.html")

@app.route("/login")
def login():
    # FIX: Behebt den "Cannot GET /login" Fehler
    scope = "identify guilds"
    url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI.replace(':', '%3A').replace('/', '%2F')}&response_type=code&scope={scope.replace(' ', '+')}"
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    res = requests.post("https://discord.com/api/oauth2/token", data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI
    }).json()
    if "access_token" in res: session["token"] = res["access_token"]
    return redirect("/")

@app.route("/api/me")
def me():
    if "token" not in session: return jsonify({"error": "unauthorized"}), 401
    r = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {session['token']}"})
    return jsonify(r.json())

@app.route("/api/guilds")
def guilds():
    if "token" not in session: return jsonify([]), 401
    r = requests.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {session['token']}"})
    return jsonify([g for g in r.json() if (int(g['permissions']) & 0x8) == 0x8])

@app.route("/api/config/<guild_id>")
def get_cfg(guild_id): return jsonify(_load().get(str(guild_id), {}))

@app.route("/api/save/<guild_id>", methods=["POST"])
def save_cfg(guild_id):
    configs = _load()
    configs[str(guild_id)] = request.json
    _save(configs)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(port=5000, debug=True)