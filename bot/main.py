import discord
from discord.ext import commands
import os
import asyncio
import logging
import sys
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# 1. LOGGING SETUP
# Damit du im Render-Dashboard genau siehst, was geladen wird.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 2. RENDER PORT FIX (Dummy Server)
# Verhindert, dass Render den Bot abschaltet, weil kein Port offen ist.
app = Flask(__name__)

@app.route('/')
def home():
    return "NeonBot Core is Live!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 3. BOT INITIALISIERUNG
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class NeonBot(commands.Bot):
    def __init__(self):
        # Intents müssen im Discord Developer Portal aktiv sein!
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            help_command=None
        )

    async def setup_hook(self):
        """Wird aufgerufen, bevor der Bot sich verbindet. Ideal zum Laden von Cogs."""
        
        # PFAD-LOGIK: Wir finden das Hauptverzeichnis (Root)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Falls main.py in /bot/ liegt, gehen wir eine Ebene höher
        root_dir = os.path.dirname(current_dir) if "bot" in current_dir else current_dir
        
        # Das Hauptverzeichnis für Python-Importe registrieren
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
            
        cogs_dir = os.path.join(root_dir, "cogs")
        logging.info(f"📂 Starte automatischen Scan im Ordner: {cogs_dir}")

        # AUTOMATISCHES LADEN
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py"):
                    try:
                        # Lädt die Datei als Erweiterung (z.B. cogs.settings)
                        cog_name = f"cogs.{filename[:-3]}"
                        await self.load_extension(cog_name)
                        logging.info(f"✅ Modul erfolgreich geladen: {filename}")
                    except Exception as e:
                        logging.error(f"❌ Fehler beim Laden von {filename}: {e}")
        else:
            logging.error(f"⚠️ KRITISCH: Ordner '{cogs_dir}' wurde nicht gefunden!")

        # GLOBALER SYNC
        # Pusht alle geladenen Befehle aus den Cogs direkt zu Discord.
        logging.info("⏳ Synchronisiere Slash-Commands global...")
        try:
            synced = await self.tree.sync()
            logging.info(f"🌐 {len(synced)} Befehle wurden erfolgreich synchronisiert!")
        except Exception as e:
            logging.error(f"❌ Globaler Sync fehlgeschlagen: {e}")

    async def on_ready(self):
        logging.info(f"🚀 Bot ist online! Eingeloggt als {self.user}")
        await self.change_presence(activity=discord.Game(name="Scanning Cogs..."))

# 4. START-LOGIK
async def run_bot():
    # Flask-Server in separatem Thread starten
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    bot = NeonBot()
    
    if not TOKEN:
        logging.error("❌ Kein DISCORD_TOKEN gefunden!")
        return

    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logging.info("Bot-Prozess durch Benutzer beendet.")