import discord
from discord.ext import commands
import os
import asyncio
import logging
import sys
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- RENDER WEB SERVER FIX ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot ist online!"
def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT SETUP ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # 1. PFAD ZUM COGS ORDNER FINDEN (Automatisch)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir) if "bot" in base_dir else base_dir
        cogs_dir = os.path.join(root_dir, "cogs")
        
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

        logging.info(f"📂 Lade DEN GANZEN ORDNER aus: {cogs_dir}")

        # 2. ALLE DATEIEN LADEN (ohne sie beim Namen zu nennen)
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        logging.info(f"✅ Geladen: {filename}")
                    except Exception as e:
                        logging.error(f"❌ Bug in {filename}: {e}")
        else:
            logging.error(f"⚠️ ORDNER NICHT GEFUNDEN: {cogs_dir}")

        # 3. GLOBAL SYNC
        logging.info("⏳ Commands werden global synchronisiert...")
        try:
            synced = await self.tree.sync()
            logging.info(f"🌐 {len(synced)} Befehle aus dem Ordner erfolgreich hochgeladen!")
        except Exception as e:
            logging.error(f"❌ Sync Error: {e}")

    async def on_ready(self):
        logging.info(f"🚀 {self.user} ist online!")
        # HIER WIRD DEIN STATUS GESETZT:
        await self.change_presence(activity=discord.Game(name="/help"))

async def run_bot():
    Thread(target=run_flask, daemon=True).start()
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(run_bot())