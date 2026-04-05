import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

import requests


class Storage:
    """Supabase-Storage über REST, kompatibel mit Python 3.14."""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.permissions_file = self.base_dir / "permissions.json"
        self._refresh_config()

    def _refresh_config(self) -> None:
        self.supabase_url = os.getenv("SUPABASE_URL", "https://yhynqarltjcnklutrwlf.supabase.co").rstrip("/")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        if not self.supabase_key:
            print("WARNUNG: Kein Supabase API-Schlüssel gefunden. Setze SUPABASE_SERVICE_KEY oder SUPABASE_ANON_KEY.")

    def _build_url(self, table: str) -> str:
        return f"{self.supabase_url}/rest/v1/{table}"

    def _safe_request(self, method: str, url: str, params=None, data=None) -> Any:
        self._refresh_config()
        try:
            response = requests.request(method, url, headers=self.headers, params=params, json=data, timeout=10)
            response.raise_for_status()
            if response.status_code in (204, 205):
                return None
            if response.text:
                return response.json()
            return None
        except requests.RequestException as exc:
            print(f"Supabase request failed: {method} {url} -> {exc}")
            return None

    # ===== WARNs =====
    def add_warn(self, guild_id: int, member_id: int, moderator_id: int, reason: str) -> int:
        payload = {
            "guild_id": guild_id,
            "member_id": member_id,
            "moderator_id": moderator_id,
            "reason": reason[:100],
            "ts": datetime.utcnow().isoformat(),
        }
        self._safe_request("POST", self._build_url("warns"), data=[payload])

        rows = self._safe_request(
            "GET",
            self._build_url("warns"),
            params={"select": "id", "guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}"},
        )
        return len(rows or [])

    def get_warns(self, guild_id: int, member_id: int) -> List[Dict[str, Any]]:
        rows = self._safe_request(
            "GET",
            self._build_url("warns"),
            params={"select": "moderator_id,reason,ts", "guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}", "order": "ts.desc"},
        )
        if not rows:
            return []
        return [{"moderator": r["moderator_id"], "reason": r["reason"], "timestamp": r["ts"]} for r in rows]

    def get_guild_warns(self, guild_id: int) -> Dict[str, List[Dict[str, Any]]]:
        rows = self._safe_request(
            "GET",
            self._build_url("warns"),
            params={"select": "member_id,moderator_id,reason,ts", "guild_id": f"eq.{guild_id}"},
        )
        if not rows:
            return {}
        warns_dict: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            member_id = str(r["member_id"])
            warns_dict.setdefault(member_id, []).append(
                {"moderator": r["moderator_id"], "reason": r["reason"], "timestamp": r["ts"]}
            )
        return warns_dict

    def remove_warn(self, guild_id: int, member_id: int, index: int) -> bool:
        rows = self._safe_request(
            "GET",
            self._build_url("warns"),
            params={"select": "id", "guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}", "order": "ts.desc"},
        )
        if not rows or index < 0 or index >= len(rows):
            return False
        warn_id = rows[index]["id"]
        self._safe_request("DELETE", self._build_url("warns"), params={"id": f"eq.{warn_id}"})
        return True

    def clear_warns(self, guild_id: int, member_id: int) -> None:
        self._safe_request(
            "DELETE",
            self._build_url("warns"),
            params={"guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}"},
        )

    # ===== PERMISSIONS =====
    def get_permissions(self) -> Dict[str, Any]:
        local_permissions = self._read_local_permissions()
        row = self._safe_request(
            "GET",
            self._build_url("config"),
            params={"select": "data", "key": "eq.permissions"},
        )
        if row and isinstance(row, list) and row:
            remote_permissions = self._normalize_permissions(row[0].get("data"))
            return self._merge_permissions(local_permissions, remote_permissions)
        return local_permissions

    def save_permissions(self, permissions: Dict[str, Any]) -> None:
        normalized = self._normalize_permissions(permissions)
        self._write_local_permissions(normalized)
        existing = self._safe_request(
            "GET",
            self._build_url("config"),
            params={"select": "id", "key": "eq.permissions"},
        )
        payload = {"key": "permissions", "data": normalized}
        if existing:
            self._safe_request("PATCH", self._build_url("config"), params={"key": "eq.permissions"}, data=payload)
        else:
            self._safe_request("POST", self._build_url("config"), data=[payload])

    @staticmethod
    def _default_permissions() -> Dict[str, Any]:
        return {"owner": [], "admins": [], "developers": [], "banned_servers": [], "banned_users": []}

    def _read_local_permissions(self) -> Dict[str, Any]:
        if not self.permissions_file.exists():
            return self._default_permissions()
        try:
            with self.permissions_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return self._normalize_permissions(data)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"WARNUNG: Konnte lokale permissions.json nicht lesen: {exc}")
            return self._default_permissions()

    def _write_local_permissions(self, permissions: Dict[str, Any]) -> None:
        try:
            with self.permissions_file.open("w", encoding="utf-8") as file:
                json.dump(permissions, file, ensure_ascii=True, indent=4)
                file.write("\n")
        except OSError as exc:
            print(f"WARNUNG: Konnte lokale permissions.json nicht schreiben: {exc}")

    def _normalize_permissions(self, permissions: Dict[str, Any] | None) -> Dict[str, Any]:
        data = self._default_permissions()
        if isinstance(permissions, dict):
            for key in data:
                value = permissions.get(key, [])
                data[key] = value if isinstance(value, list) else []
        return data

    def _merge_permissions(self, local_permissions: Dict[str, Any], remote_permissions: Dict[str, Any]) -> Dict[str, Any]:
        merged = self._default_permissions()
        for key in merged:
            local_values = local_permissions.get(key, [])
            remote_values = remote_permissions.get(key, [])
            merged[key] = list(dict.fromkeys([*local_values, *remote_values]))
        return merged

