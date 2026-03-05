import os
import json
from flask import Flask, session, redirect, url_for, request, jsonify, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase Setup
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'geheim')

# [Restliche OAuth2 Logik wie zuvor...]
# Hier nur die geänderten API Endpunkte:

@app.route('/api/guild/<guild_id>/config', methods=['GET', 'POST'])
def guild_config(guild_id):
    if request.method == 'GET':
        # Daten von Supabase holen
        response = supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        if response.data:
            return jsonify(response.data[0]['config'])
        return jsonify({})
    
    if request.method == 'POST':
        new_config = request.json.get('config')
        module = request.json.get('module')
        
        # Erst aktuelle Config holen, dann mergen
        current = supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        full_config = current.data[0]['config'] if current.data else {}
        full_config[module] = new_config
        
        # In Supabase speichern (Upsert = Update oder Insert)
        supabase.table("server_configs").upsert({"guild_id": str(guild_id), "config": full_config}).execute()
        return jsonify({"status": "saved"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))