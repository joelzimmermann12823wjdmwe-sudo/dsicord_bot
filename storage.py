import os
from datetime import datetime
from typing import Any, Dict, List
from supabase import create_client, Client

# Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yhynqarltjcnklutrwlf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class Storage:
    """Optimierte Speicherklasse für Supabase - minimalistisches Design"""

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Stelle sicher, dass Tabellen existieren (einmalig beim Start)"""
        try:
            # Versuche eine Query, um zu prüfen, ob Tabellen existieren
            supabase.table("warns").select("*", count="exact").limit(1).execute()
        except Exception as e:
            print(f"Info: Tabellen werden bei Bedarf erstellt. {e}")

    # ===== WARNS =====
    def add_warn(self, guild_id: int, member_id: int, moderator_id: int, reason: str) -> int:
        """Füge einen Warn hinzu und gebe die neue Anzahl zurück"""
        data = {
            "guild_id": guild_id,
            "member_id": member_id,
            "moderator_id": moderator_id,
            "reason": reason[:100],  # Max 100 chars = sparsam
            "ts": datetime.utcnow().isoformat(),
        }
        supabase.table("warns").insert(data).execute()
        
        # Zähle Warns für diesen User
        result = supabase.table("warns").select("*", count="exact").eq("member_id", member_id).eq("guild_id", guild_id).execute()
        return result.count if result.count else 0

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

