import json, os
from pathlib import Path
P = Path(__file__).parent.parent.parent / "data" / "guild_configs.json"
def is_enabled(gid, mod):
    if not P.exists(): return True
    with open(P, encoding="utf-8") as f:
        return json.load(f).get(str(gid), {}).get(mod, {}).get("enabled", True)