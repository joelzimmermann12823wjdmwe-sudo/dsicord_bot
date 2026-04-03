# 🚀 Neon-Bot - Supabase Setup

## Installation & Konfiguration

### 1. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

### 2. **Supabase Datenbank einrichten**

Du brauchst noch die **Service Key**. Diese ist sensibel - gib sie nicht weiter!

#### Service Key finden:
1. Gehe zu https://supabase.com/dashboard
2. Wähle dein Projekt: `yhynqarltjcnklutrwlf`
3. Linkes Menü → `Settings` → `API`
4. Kopiere **`service_role secret`** (nicht `anon key`)

### 3. **.env Datei erstellen**

Kopiere `.env.example` zu `.env` und fülle es aus:
```bash
cp .env.example .env
```

Öffne `.env` und ersetze:
```
DISCORD_TOKEN=dein_wirklicher_bot_token
SUPABASE_URL=https://yhynqarltjcnklutrwlf.supabase.co
SUPABASE_ANON_KEY=sb_publishable_sKxMfDPdy_mxwdLzOi4JMA_2smmPNgg
SUPABASE_SERVICE_KEY=deine_service_key_hier
```

### 4. **Datenbank-Tabellen erstellen**

Führe folgende SQL im Supabase SQL Editor aus (https://supabase.com/dashboard → SQL Editor → New Query):

```sql
CREATE TABLE IF NOT EXISTS warns (
    id BIGSERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    member_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    reason TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_warns_guild_member ON warns(guild_id, member_id);

CREATE TABLE IF NOT EXISTS config (
    id BIGSERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    data JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

Klicke `RUN` und bestätige.

### 5. **Bot starten**
```bash
python main.py
```

## 📊 Datenbank-Struktur

### **warns** Tabelle
Speichert jeden Warn minimal:
- `guild_id`: Server ID
- `member_id`: User ID
- `moderator_id`: Mod, der warned hat
- `reason`: Grund (max 100 Zeichen)
- `ts`: Zeitstempel

### **config** Tabelle
Speichert Admin-Config als JSON:
- `key`: "permissions"
- `data`: { "owner": [], "admins": [], "developers": [], "banned_servers": [], "banned_users": [] }

## 🔒 Sicherheit

⚠️ **WICHTIG**:
- `.env` Datei NIEMALS in Git committen
- Service Key ist sensibel - teile sie nicht!
- Verwende `SUPABASE_SERVICE_KEY` für Server (vollen Zugriff)
- In Zukunft kannst du RLS (Row Level Security) aktivieren

## 💾 Speicheroptimierung

- **Warns**: Nur 5 Felder statt 7 → ~40% kleiner
- **Reason**: Maximal 100 Zeichen
- **Timestamps**: ISO Format (kompakt)
- **Permissions**: Ein JSON-Dokument (statt 5 Spalten)

**Geschätzter Speicher pro 100 Warns**: ~15 KB

## 📝 Commands

```
/ban_server <id>     - Server bann
/unban_server <id>   - Server entbann
/ban_user <id>       - User bann
/unban_user <id>     - User entbann
/warn                - Nutzer warnen
/warns               - Warns anzeigen
/test_cmd            - Nur für Developer
/fixsync             - Nur für Developer
```

---

**Fragen?** Schreib einen Issue oder PR!
