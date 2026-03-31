import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class Storage:
    def __init__(self, path: str = "storage.bin"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"warns": {}}

        try:
            with self.path.open("rb") as file:
                data = pickle.load(file)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        return {"warns": {}}

    def _save(self) -> None:
        with self.path.open("wb") as file:
            pickle.dump(self._data, file)

    def _ensure_warns(self) -> None:
        if "warns" not in self._data or not isinstance(self._data["warns"], dict):
            self._data["warns"] = {}

    def add_warn(self, guild_id: int, member_id: int, moderator_id: int, reason: str) -> int:
        self._ensure_warns()
        guild_warns = self._data["warns"].setdefault(str(guild_id), {})
        member_warns = guild_warns.setdefault(str(member_id), [])
        member_warns.append(
            {
                "moderator": moderator_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self._save()
        return len(member_warns)

    def get_warns(self, guild_id: int, member_id: int) -> List[Dict[str, Any]]:
        self._ensure_warns()
        return self._data["warns"].get(str(guild_id), {}).get(str(member_id), [])

    def get_guild_warns(self, guild_id: int) -> Dict[str, List[Dict[str, Any]]]:
        self._ensure_warns()
        return self._data["warns"].get(str(guild_id), {})

    def clear_warns(self, guild_id: int, member_id: int) -> None:
        self._ensure_warns()
        guild_warns = self._data["warns"].get(str(guild_id), {})
        if str(member_id) in guild_warns:
            del guild_warns[str(member_id)]
            self._save()
