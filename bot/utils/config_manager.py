import json
import os
from pathlib import Path

# Fix: Dynamische Pfadfindung für Linux (Render) und Windows
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "data" / "guild_configs.json"

def load_config(guild_id):
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get(str(guild_id), {})
    except:
        return {}

def save_config(guild_id, module, settings):
    data = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: data = {}
    
    if str(guild_id) not in data: data[str(guild_id)] = {}
    data[str(guild_id)][module] = settings
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
