import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import logging
import sys

# Logging Setup
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT BINDING (Dummy Server) ---
app = Flask(__name__)
@app.route('/')
def home(): return "NeonBot is Live!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT SETUP ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class NeonBot(commands.Bot):
    def __init__(self):
        # WICHTIG: Stelle sicher, dass Presence/Members/Message Intents im Portal AN sind!
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Dynamische Pfadsuche für Cogs
        possible_paths = [
            os.path.join(os.getcwd(), "cogs"),
            os.path.join(os.getcwd(), "bot", "cogs"),
            os.path.join(os.path.dirname(__file__), "cogs")
        ]
        
        cogs_dir = None
        for path in possible_paths:
            if os.path.exists(path):
                cogs_dir = path
                break
        
        if cogs_dir:
            logging.info(f"📂 Lade Cogs aus: {cogs_dir}")
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py"):
                    cog_name = f"cogs.{filename[:-3]}"
                    # Falls der Ordnerpfad tiefer liegt, passen wir den Import an
                    try:
                        await self.load_extension(cog_name)
                        logging.info(f"✅ Cog geladen: {filename}")
                    except Exception as e:
                        logging.error(f"❌ Fehler bei {filename}: {e}")
        else:
            logging.error("❌ KRITISCH: Kein 'cogs' Ordner gefunden!")

        # Globaler Sync
        logging.info("⏳ Synchronisiere Slash-Commands global...")
        await self.tree.sync()
        logging.info("🌐 Globaler Sync abgeschlossen!")

    async def on_ready(self):
        logging.info(f"🚀 Bot online als {self.user}")

async def run_all():
    # Flask Server für Render starten
    Thread(target=run_flask, daemon=True).start()
    
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    if not TOKEN:
        logging.error("❌ TOKEN fehlt!")
    else:
        asyncio.run(run_all())