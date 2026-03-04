from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>NeonBot Dashboard ist online!</h1><p>Der Bot läuft im Hintergrund.</p>"

if __name__ == "__main__":
    # WICHTIG: Render gibt den Port vor, Flask muss darauf hören
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)