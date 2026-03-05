import discord
from discord.ext import commands
import os
import asyncio
import logging
import sys
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# 1. LOGGING SETUP (Wichtig für Render-Logs)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 2. RENDER PORT BINDING (Verhindert "No open ports detected")
app = Flask(__name__)

@app.route('/')
def home():
    return "NeonBot is Live and Running!"

def run_flask():
    # Render vergibt den Port dynamisch über die Umgebungsvariable PORT
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🌐 Starte Webserver auf Port {port}...")
    app.run(host='0.0.0.0', port=port)

# 3. BOT INITIALISIERUNG
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class NeonBot(commands.Bot):
    def __init__(self):
        # WICHTIG: Stelle sicher, dass Presence/Members/Message Intents im Discord Portal AN sind!
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            help_command=None
        )

    async def setup_hook(self):
        # PFAD-FIX: Ermittle das Hauptverzeichnis (eins über /bot/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        
        # Füge das Hauptverzeichnis zum Python-Pfad hinzu, damit 'cogs' gefunden wird
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        
        cogs_dir = os.path.join(root_dir, "cogs")
        logging.info(f"📂 Suche Cogs in: {cogs_dir}")

        # Cogs laden
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py"):
                    cog_path = f"cogs.{filename[:-3]}"
                    try:
                        await self.load_extension(cog_name := cog_path)
                        logging.info(f"✅ Cog geladen: {filename}")
                    except Exception as e:
                        logging.error(f"❌ Fehler beim Laden von {filename}: {e}")
        else:
            logging.error(f"⚠️ KRITISCH: Ordner {cogs_dir} nicht gefunden!")

        # GLOBAL SLASH COMMAND SYNC
        try:
            logging.info("⏳ Synchronisiere Slash-Commands global (das kann kurz dauern)...")
            synced = await self.tree.sync()
            logging.info(f"🌐 {len(synced)} Slash-Commands wurden GLOBAL synchronisiert!")
        except Exception as e:
            logging.error(f"❌ Globaler Sync fehlgeschlagen: {e}")

    async def on_ready(self):
        logging.info(f"🚀 Bot erfolgreich eingeloggt als {self.user} (ID: {self.user.id})")
        # Setzt einen Status
        await self.change_presence(activity=discord.Game(name="/settings | NeonBot"))

# 4. START-LOGIK
async def start_bot():
    # Starte Flask in einem separaten Thread (Daemon sorgt dafür, dass er mit dem Bot stirbt)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    bot = NeonBot()
    
    if not TOKEN:
        logging.error("❌ DISCORD_TOKEN nicht in der .env oder den Render-Settings gefunden!")
        return

    async with bot:
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            logging.error("❌ Login fehlgeschlagen! Der Token ist ungültig.")
        except Exception as e:
            logging.error(f"❌ Ein kritischer Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logging.info("👋 Bot wird heruntergefahren...")