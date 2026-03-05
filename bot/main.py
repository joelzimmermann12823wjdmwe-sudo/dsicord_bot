import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- DUMMY SERVER FÜR RENDER PORT FIX ---
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"

def run_flask():
    # Render nutzt oft Port 10000, wir nehmen den aus der Umgebungsvariable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIK ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Pfad-Fix: Wir finden heraus, wo DIESE Datei liegt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Wir suchen den cogs Ordner entweder im aktuellen Verzeichnis oder eins drüber
COGS_DIR = os.path.join(BASE_DIR, "cogs")

if not os.path.exists(COGS_DIR):
    # Falls main.py in einem Unterordner wie /bot/ liegt, schauen wir eine Ebene höher
    COGS_DIR = os.path.join(os.path.dirname(BASE_DIR), "cogs")

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        print(f"Suche Cogs in: {COGS_DIR}")
        if os.path.exists(COGS_DIR):
            for filename in os.listdir(COGS_DIR):
                if filename.endswith(".py"):
                    try:
                        # Wir laden die Extension mit dem vollen Pfad
                        await self.load_extension(f"cogs.{filename[:-3]}")
                        print(f"✅ {filename} geladen")
                    except Exception as e:
                        print(f"❌ Fehler bei {filename}: {e}")
        else:
            print(f"⚠️ KRITISCH: Ordner {COGS_DIR} wurde nicht gefunden!")

    async def on_ready(self):
        print(f"✅ Bot {self.user} ist ONLINE!")

async def main():
    # Startet den Port-Server für Render
    Thread(target=run_flask, daemon=True).start()
    
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass