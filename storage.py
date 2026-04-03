import os
import json
from datetime import datetime
from typing import Any, Dict, List

import requests

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yhynqarltjcnklutrwlf.supabase.co").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def _build_url(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"


def _safe_request(method: str, url: str, params=None, data=None) -> Any:
    try:
        r = requests.request(method, url, headers=HEADERS, params=params, json=data, timeout=15)
        r.raise_for_status()
        if r.status_code in (204, 205):
            return None
        if r.text:
            return r.json()
        return None
    except requests.RequestException as e:
        print(f"Supabase request failed: {method} {url} -> {e}")
        return None


class Storage:
    """Supabase-Storage über REST, kompatibel mit Python 3.14."""

    def __init__(self):
        pass

    # ===== WARNS =====
    def add_warn(self, guild_id: int, member_id: int, moderator_id: int, reason: str) -> int:
        payload = {
            "guild_id": guild_id,
            "member_id": member_id,
            "moderator_id": moderator_id,
            "reason": reason[:100],
            "ts": datetime.utcnow().isoformat(),
        }
        _safe_request("POST", _build_url("warns"), data=[payload])

        rows = _safe_request(
            "GET",
            _build_url("warns"),
            params={"select": "id", "guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}"},
        )
        return len(rows or [])

    def get_warns(self, guild_id: int, member_id: int) -> List[Dict[str, Any]]:
        rows = _safe_request(
            "GET",
            _build_url("warns"),
            params={"select": "moderator_id,reason,ts", "guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}", "order": "ts.desc"},
        )
        if not rows:
            return []
        return [
            {"moderator": r["moderator_id"], "reason": r["reason"], "timestamp": r["ts"]}
            for r in rows
        ]

    def get_guild_warns(self, guild_id: int) -> Dict[str, List[Dict[str, Any]]]:
        rows = _safe_request(
            "GET",
            _build_url("warns"),
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
        rows = _safe_request(
            "GET",
            _build_url("warns"),
            params={"select": "id", "guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}", "order": "ts.desc"},
        )
        if not rows or index < 0 or index >= len(rows):
            return False
        warn_id = rows[index]["id"]
        _safe_request("DELETE", _build_url("warns"), params={"id": f"eq.{warn_id}"})
        return True

    def clear_warns(self, guild_id: int, member_id: int) -> None:
        _safe_request(
            "DELETE",
            _build_url("warns"),
            params={"guild_id": f"eq.{guild_id}", "member_id": f"eq.{member_id}"},
        )

    # ===== PERMISSIONS =====
    def get_permissions(self) -> Dict[str, Any]:
        row = _safe_request(
            "GET",
            _build_url("config"),
            params={"select": "data", "key": "eq.permissions"},
        )
        if row and isinstance(row, list) and row:
            return row[0].get("data", self._default_permissions())
        return self._default_permissions()

    def save_permissions(self, permissions: Dict[str, Any]) -> None:
        existing = _safe_request(
            "GET",
            _build_url("config"),
            params={"select": "id", "key": "eq.permissions"},
        )
        payload = {"key": "permissions", "data": permissions}
        if existing:
            _safe_request("PATCH", _build_url("config"), params={"key": "eq.permissions"}, data=payload)
        else:
            _safe_request("POST", _build_url("config"), data=[payload])

    @staticmethod
    def _default_permissions() -> Dict[str, Any]:
        return {"owner": [], "admins": [], "developers": [], "banned_servers": [], "banned_users": []}

    def get_warns(self, guild_id: int, member_id: int) -> List[Dict[str, Any]]:
        """Hole alle Warns für einen User"""
        try:
            result = supabase.table("warns").select("*").eq("guild_id", guild_id).eq("member_id", member_id).order("ts", desc=True).execute()
            return [
                {
                    "moderator": row["moderator_id"],
                    "reason": row["reason"],
                    "timestamp": row["ts"],
                }
                for row in result.data
            ]
        except Exception:
            return []

    def get_guild_warns(self, guild_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Hole alle Warns für einen Server - für Statistiken/Admin"""
        try:
            result = supabase.table("warns").select("*").eq("guild_id", guild_id).execute()
            warns_dict = {}
            for row in result.data:
                member_id = str(row["member_id"])
                if member_id not in warns_dict:
                    warns_dict[member_id] = []
                warns_dict[member_id].append({
                    "moderator": row["moderator_id"],
                    "reason": row["reason"],
                    "timestamp": row["ts"],
                })
            return warns_dict
        except Exception:
            return {}

    def remove_warn(self, guild_id: int, member_id: int, index: int) -> bool:
        """Entferne einen Warn (nach Index in sortierter Liste)"""
        try:
            warns = supabase.table("warns").select("id").eq("guild_id", guild_id).eq("member_id", member_id).order("ts", desc=True).execute()
            if index < len(warns.data):
                warn_id = warns.data[index]["id"]
                supabase.table("warns").delete().eq("id", warn_id).execute()
                return True
        except Exception:
            pass
        return False

    def clear_warns(self, guild_id: int, member_id: int) -> None:
        """Lösche alle Warns für einen User"""
        try:
            supabase.table("warns").delete().eq("guild_id", guild_id).eq("member_id", member_id).execute()
        except Exception:
            pass

    # ===== PERMISSIONS =====
    def get_permissions(self) -> Dict[str, Any]:
        """Hole Permissions-Config"""
        try:
            result = supabase.table("config").select("data").eq("key", "permissions").execute()
            if result.data:
                return result.data[0].get("data", self._default_permissions())
        except Exception:
            pass
        return self._default_permissions()

    def save_permissions(self, permissions: Dict[str, Any]) -> None:
        """Speichere Permissions-Config"""
        try:
            # Prüfe ob Eintrag existiert
            existing = supabase.table("config").select("id").eq("key", "permissions").execute()
            if existing.data:
                # Update
                supabase.table("config").update({"data": permissions}).eq("key", "permissions").execute()
            else:
                # Insert
                supabase.table("config").insert({"key": "permissions", "data": permissions}).execute()
        except Exception as e:
            print(f"Fehler beim Speichern von Permissions: {e}")

    @staticmethod
    def _default_permissions() -> Dict[str, Any]:
        return {"owner": [], "admins": [], "developers": [], "banned_servers": [], "banned_users": []}

