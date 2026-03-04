import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "guild_configs.json"

def load_config(guild_id):
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get(str(guild_id), {})

def save_config(guild_id, module, settings):
    data = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    if str(guild_id) not in data:
        data[str(guild_id)] = {}
    
    data[str(guild_id)][module] = settings
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
