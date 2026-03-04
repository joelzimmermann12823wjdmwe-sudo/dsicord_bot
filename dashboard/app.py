from flask import Flask, render_template, request, jsonify, session, redirect
import os
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "neon_secret_123")
CONFIG_DIR = Path(__file__).parent.parent / "data"
CONFIG_FILE = CONFIG_DIR / "guild_configs.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/guild/<guild_id>/config", methods=["GET", "POST"])
def manage_config(guild_id):
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f: json.dump({}, f)
    
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)

    if request.method == "POST":
        req = request.json
        module = req.get("module")
        config = req.get("config")
        
        if str(guild_id) not in data: data[str(guild_id)] = {}
        data[str(guild_id)][module] = config
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return jsonify({"ok": True})

    return jsonify(data.get(str(guild_id), {}))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
