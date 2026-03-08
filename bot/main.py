Dieser Fehler tritt auf, weil Python über das Sonderzeichen "ü" in deinem Kommentar stolpert und die Datei nicht als UTF-8 erkennt. In der Programmierung sollten Umlaute in Kommentaren vermieden werden, um genau solche Deployment-Fehler zu verhindern.

Ich habe die main.py korrigiert (alle Umlaute entfernt) und so optimiert, dass sie den gesamten Ordner automatisch lädt und für 1.000+ Server bereit ist.

1. Die korrigierte bot/main.py (Kopieren & Ersetzen)
Python

# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
import asyncio
import logging
import sys
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- RENDER WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "NeonBot Online"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT SETUP ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# AutoShardedBot fuer Skalierung auf 1000+ Server
class NeonBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Pfad-Logik fuer Cogs Ordner
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir) if "bot" in current_dir else current_dir
        
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
            
        cogs_dir = os.path.join(root_dir, "cogs")
        logging.info(f"Scanne Ordner: {cogs_dir}")

        # Lade JEDE Datei im Cogs Ordner automatisch
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        logging.info(f"Geladen: {filename}")
                    except Exception as e:
                        logging.error(f"Fehler in {filename}: {e}")

        # Globaler Sync aller Commands
        await self.tree.sync()

    async def on_ready(self):
        logging.info(f"Bot bereit als {self.user}")
        # Status setzen
        await self.change_presence(activity=discord.Game(name="/help"))

async def run():
    Thread(target=run_flask, daemon=True).start()
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(run())