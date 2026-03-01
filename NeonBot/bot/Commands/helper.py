import json
from pathlib import Path

# NeonBot/bot/Commands/helper.py
# 3x .parent = NeonBot/
# / "data"   = NeonBot/data/
DATA = Path(__file__).resolve().parent.parent.parent / "data"
DATA.mkdir(exist_ok=True)


def load_data(file: str) -> dict:
    path = DATA / file
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_data(file: str, data) -> None:
    try:
        with open(DATA / file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except OSError as e:
        print(f"[FEHLER] save_data({file}): {e}")


def is_module_enabled(guild_id, module: str) -> bool:
    return load_data("config.json").get(str(guild_id), {}).get(f"module_{module}", False)


def get_log_channel_id(guild_id):
    return load_data("config.json").get(str(guild_id), {}).get("log_channel")
