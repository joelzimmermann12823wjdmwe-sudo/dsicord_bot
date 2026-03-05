import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import logging

# Logging für Render-Dashboard
logging.basicConfig(level=logging.INFO)

# --- RENDER PORT BINDING ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT SETUP ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class NeonBot(commands.Bot):
    def __init__(self):
        # WICHTIG: Intents müssen im Developer Portal aktiv sein!
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # 1. Cogs laden
        # Wir suchen den Ordner relativ zum Speicherort dieser Datei
        base_path = os.path.dirname(os.path.abspath(__file__))
        cogs_path = os.path.join(base_path, "cogs")
        
        if os.path.exists(cogs_path):
            for filename in os.listdir(cogs_path):
                if filename.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        logging.info(f"✅ Cog geladen: {filename}")
                    except Exception as e:
                        logging.error(f"❌ Fehler bei {filename}: {e}")
        
        # 2. GLOBAL SYNC FIX
        # Das hier erzwingt die Synchronisation mit den Discord-Servern
        try:
            logging.info("⏳ Synchronisiere Slash-Commands global...")
            synced = await self.tree.sync()
            logging.info(f"✅ {len(synced)} Slash-Commands wurden GLOBAL synchronisiert!")
        except Exception as e:
            logging.error(f"❌ Globaler Sync fehlgeschlagen: {e}")

    async def on_ready(self):
        logging.info(f"🚀 {self.user} ist jetzt online und bereit!")

async def start():
    # Flask in separatem Thread starten
    Thread(target=run_flask, daemon=True).start()
    
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    if not TOKEN:
        logging.error("❌ DISCORD_TOKEN fehlt in den Umgebungsvariablen!")
    else:
        asyncio.run(start())