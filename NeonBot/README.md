# ⚡ Neon Bot

Dein professioneller Discord Moderations-Bot mit Web-Dashboard!

## 📁 Projektstruktur

NeonBot/
├── .env                    ← Deine Tokens (NICHT teilen!)
├── requirements.txt
├── start_bot.bat           ← Bot starten (Windows)
├── start_website.bat       ← Website starten (Windows)
├── bot/
│   ├── main.py             ← Bot Hauptdatei
│   └── Commands/
│       ├── moderation.py   ← /ban /kick /mute /warn etc.
│       ├── tickets.py      ← Ticket System
│       ├── logging.py      ← Event Logging
│       ├── info.py         ← /help /userinfo /serverinfo
│       ├── welcome.py      ← Willkommens-Nachrichten
│       └── automod.py      ← Automatische Moderation
├── data/
│   ├── config.json         ← Server Einstellungen
│   ├── tickets.json        ← Ticket Daten
│   ├── warnings.json       ← Verwarnungen
│   └── logs.json           ← Logs
└── website/
    ├── app.py              ← Flask Website
    ├── templates/          ← HTML Templates
    └── static/             ← CSS & JS

## 🚀 Setup

### 1. Python Pakete installieren
`bash
cd NeonBot
pip install -r requirements.txt
`

### 2. .env ausfuellen
Oeffne die .env Datei und fuege folgende Werte ein:
- DISCORD_TOKEN → Dein Bot Token (discord.com/developers)
- DISCORD_CLIENT_ID → Application ID
- DISCORD_CLIENT_SECRET → OAuth2 Secret
- GUILD_ID → Deine Server ID
- FLASK_SECRET_KEY → Irgendein langer zufaelliger Text

### 3. Discord Developer Portal
- Gehe zu discord.com/developers/applications
- Erstelle eine neue Application
- Gehe zu "Bot" → Token kopieren
- Gehe zu "OAuth2" → Redirect URI hinzufuegen: http://localhost:5000/callback

### 4. Bot starten
`bash
# Bot:
cd bot && python main.py

# Website:
cd website && python app.py
`

### 5. Bot einladen
Link: https://discord.com/api/oauth2/authorize?client_id=DEINE_CLIENT_ID&permissions=8&scope=bot%20applications.commands

## 🔧 Befehle
- /ban, /unban, /kick, /mute, /unmute
- /warn, /warns
- /clear, /slowmode
- /ticket-setup
- /setlog, /setwelcome
- /help, /botinfo, /userinfo, /serverinfo

## 🌐 Website
Oeffne http://localhost:5000 und logge dich mit Discord ein!
