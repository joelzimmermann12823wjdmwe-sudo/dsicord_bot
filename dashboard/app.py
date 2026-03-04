from flask import Flask, render_template, request, redirect, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "neon_secret_321")

# Deine Daten von Discord (müssen bei Render als Environment Variables rein!)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://dsicord-bot-c4md.onrender.com"

@app.route("/")
def index():
    code = request.args.get("code")
    if code:
        # Hier würde man den Code gegen einen Token tauschen
        return f"<h1>Login erfolgreich!</h1><p>Code erhalten: {code}</p>"
    return "<h1>NeonBot Dashboard</h1><p>Bitte logge dich über Discord ein.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)