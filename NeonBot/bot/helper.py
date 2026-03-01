import json
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
DATA.mkdir(exist_ok=True)

def load_data(file: str):
    path = DATA / file
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(file: str, data):
    with open(DATA / file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
