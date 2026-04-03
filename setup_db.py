#!/usr/bin/env python3
"""
Setup-Skript für Supabase-Datenbank
Führe dieses Skript einmal aus: python setup_db.py
"""

import os
from pathlib import Path
from supabase import create_client

# Lade .env
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Fehler: SUPABASE_URL und SUPABASE_KEY müssen in .env gesetzt sein!")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔧 Richte Supabase-Datenbank ein...")

# SQL für Tabellen erstellen
sql_commands = [
    # Warns Tabelle
    """
    CREATE TABLE IF NOT EXISTS warns (
        id BIGSERIAL PRIMARY KEY,
        guild_id BIGINT NOT NULL,
        member_id BIGINT NOT NULL,
        moderator_id BIGINT NOT NULL,
        reason TEXT NOT NULL,
        ts TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    # Index für schnellere Queries
    "CREATE INDEX IF NOT EXISTS idx_warns_guild_member ON warns(guild_id, member_id);",
    
    # Config Tabelle für Permissions etc.
    """
    CREATE TABLE IF NOT EXISTS config (
        id BIGSERIAL PRIMARY KEY,
        key TEXT UNIQUE NOT NULL,
        data JSONB NOT NULL,
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
]

print("📊 Erstelle Tabellen...")
try:
    # Hinweis: Supabase hat SQL-Editor im Dashboard
    print("⚠️  Hinweis: Um Tabellen automatisch zu erstellen, musst du diese SQL manuell im Supabase Dashboard ausführen:")
    print("\n" + "="*60)
    for i, sql in enumerate(sql_commands, 1):
        print(f"\n-- Befehl {i}:")
        print(sql.strip())
    print("\n" + "="*60)
    
    print("\n📝 Anleitung:")
    print("1. Gehe zu: https://supabase.com/dashboard")
    print("2. Wähle dein Projekt")
    print("3. Gehe zu 'SQL Editor' (linkes Menü)")
    print("4. Klicke 'New Query'")
    print("5. Kopiere die obigen SQL-Befehle rein")
    print("6. Klicke 'RUN'")
    print("\n✅ Danach ist die Datenbank bereit!")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    exit(1)
