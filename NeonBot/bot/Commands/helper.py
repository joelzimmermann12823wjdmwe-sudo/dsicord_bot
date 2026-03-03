import json
import os

DATA_PATH = "data/"

def save_json(filename, data):
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    with open(f"{DATA_PATH}{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_json(filename):
    path = f"{DATA_PATH}{filename}"
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

async def send_dm(user, embed):
    try: await user.send(embed=embed)
    except: pass
