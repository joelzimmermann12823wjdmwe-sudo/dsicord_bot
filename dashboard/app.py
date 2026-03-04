from flask import Flask, render_template, request, jsonify, session
import os

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "neon_super_secret_123")

@app.route("/")
def index():
    # Lädt deine neue index.html aus dem templates-Ordner
    return render_template("index.html")

# --- DUMMY API ENDPUNKTE (Damit das Dashboard nicht leer bleibt) ---
@app.route("/api/me")
def get_me():
    # Später durch echten Discord-Login ersetzen
    return jsonify({"username": "Admin", "id": "123", "avatar": None})

@app.route("/api/guilds")
def get_guilds():
    # Liste der Server, auf denen der Bot ist
    return jsonify([
        {"name": "Neon Test-Server", "id": "1", "icon": None, "bot_present": True}
    ])

@app.route("/api/guild/<gid>/info")
def guild_info(gid):
    return jsonify({
        "channels": [{"name": "general", "id": "101"}, {"name": "logs", "id": "102"}],
        "roles": [{"name": "Admin", "id": "201", "color": 16711680}],
        "categories": [{"name": "Support", "id": "301"}]
    })

@app.route("/api/guild/<gid>/config", methods=["GET", "POST"])
def guild_config(gid):
    return jsonify({"automod": {"warn_after": 3, "mute_after": 5}})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)