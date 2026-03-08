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

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask Server fuer Render (Keep-Alive)
app = Flask(__name__)
@app.route('/')
def home(): return "Neon Bot is Sharded & Online"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# AutoShardedBot fuer Support von 1000+ Servern
class NeonBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Pfad-Logik zum automatischen Laden des Cogs-Ordners
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir) if "bot" in current_dir else current_dir
        
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
            
        cogs_dir = os.path.join(root_dir, "cogs")
        logging.info(f"Scanning directory: {cogs_dir}")

        # Lade jede .py Datei im Ordner automatisch
        if os.path.exists(cogs_dir):
            for filename in os.listdir(cogs_dir):
                if filename.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        logging.info(f"Successfully loaded: {filename}")
                    except Exception as e:
                        logging.error(f"Failed to load {filename}: {e}")

        # Synchronisiere alle Slash-Commands global
        await self.tree.sync()

    async def on_ready(self):
        logging.info(f"Logged in as {self.user} on {len(self.guilds)} servers")
        # Status setzen: Spielt /help
        await self.change_presence(activity=discord.Game(name="/help"))

async def run():
    Thread(target=run_flask, daemon=True).start()
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(run())