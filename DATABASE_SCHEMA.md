# Neon Bot - Datenbank Schema

Diese Datei dokumentiert alle benötigten Tabellen für Supabase/PostgreSQL.

## Tabellen

### 1. guild_settings
Server-spezifische Einstellungen.

```sql
CREATE TABLE guild_settings (
    id SERIAL PRIMARY KEY,
    guild_id TEXT UNIQUE NOT NULL,
    prefix TEXT DEFAULT '!',
    welcome_msg TEXT DEFAULT 'Willkommen {user}!',
    welcome_enabled BOOLEAN DEFAULT true,
    automod_enabled BOOLEAN DEFAULT true,
    log_channel_id TEXT,
    welcome_channel_id TEXT,
    welcome_role_id TEXT,
    admin_role_id TEXT,
    mod_role_id TEXT,
    antinuke_limit INTEGER DEFAULT 10,
    welcome_image_url TEXT,
    link_filter_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. whitelist
Whitelist für Anti-Nuke und AutoMod.

```sql
CREATE TABLE whitelist (
    id SERIAL PRIMARY KEY,
    guild_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL, -- 'user', 'role', 'link'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(guild_id, target_id)
);
```

### 3. bad_words
Liste verbotener Wörter für AutoMod.

```sql
CREATE TABLE bad_words (
    id SERIAL PRIMARY KEY,
    guild_id TEXT NOT NULL,
    word TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(guild_id, word)
);
```

### 4. warns
Verwarnungen für User.

```sql
CREATE TABLE warns (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    moderator_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. bot_bans
Globale Bans für User oder Server.

```sql
CREATE TABLE bot_bans (
    id SERIAL PRIMARY KEY,
    target_id TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL, -- 'user', 'guild'
    reason TEXT DEFAULT 'Kein Grund angegeben',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. ticket_panels
Ticket-System Panels.

```sql
CREATE TABLE ticket_panels (
    id SERIAL PRIMARY KEY,
    guild_id TEXT NOT NULL,
    panel_name TEXT NOT NULL,
    support_role_id TEXT,
    channel_id TEXT,
    category_id TEXT,
    ticket_categories JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7. bot_only_channels
Kanäle, in denen nur Bot-Befehle erlaubt sind.

```sql
CREATE TABLE bot_only_channels (
    id SERIAL PRIMARY KEY,
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    UNIQUE(guild_id, channel_id)
);
```

## RLS (Row Level Security)

Aktiviere RLS für alle Tabellen:

```sql
ALTER TABLE guild_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE whitelist ENABLE ROW LEVEL SECURITY;
ALTER TABLE bad_words ENABLE ROW LEVEL SECURITY;
ALTER TABLE warns ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_bans ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_panels ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_only_channels ENABLE ROW LEVEL SECURITY;
```

Erstelle Policies (mit deinem Service Key):

```sql
CREATE POLICY "Allow all" ON guild_settings FOR ALL USING (true);
CREATE POLICY "Allow all" ON whitelist FOR ALL USING (true);
CREATE POLICY "Allow all" ON bad_words FOR ALL USING (true);
CREATE POLICY "Allow all" ON warns FOR ALL USING (true);
CREATE POLICY "Allow all" ON bot_bans FOR ALL USING (true);
CREATE POLICY "Allow all" ON ticket_panels FOR ALL USING (true);
CREATE POLICY "Allow all" ON bot_only_channels FOR ALL USING (true);
```
