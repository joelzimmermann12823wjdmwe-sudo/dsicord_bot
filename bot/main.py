import discord
from discord.ext import commands
import os, sys, asyncio, logging
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Logging ohne Umlaute fuer Render-Kompatibilitaet
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)
@app.route('/')
def home(): return "Neon Bot is Online"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

load_dotenv()

class NeonBot(commands.AutoShardedBot): # Sharding fuer 1000+ Server
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), help_command=None)

    async def setup_hook(self):
        # Dynamisches Laden des gesamten Cogs-Ordners
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir) if "bot" in base_dir else base_dir
        if root_dir not in sys.path: sys.path.insert(0, root_dir)
        
        cogs_path = os.path.join(root_dir, "cogs")
        for file in os.listdir(cogs_path):
            if file.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    print(f"Erfolg: {file} geladen")
                except Exception as e:
                    print(f"Fehler in {file}: {e}")
        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot ist bereit als {self.user}")
        await self.change_presence(activity=discord.Game(name="/help"))

async def start():
    Thread(target=run_flask, daemon=True).start()
    bot = NeonBot()
    async with bot: await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__": asyncio.run(start())
