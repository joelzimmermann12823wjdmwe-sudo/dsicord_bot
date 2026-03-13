import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- WEB SERVER FÜR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Neon Bot ist online!"

def run_webserver():
    # Render nutzt standardmäßig Port 10000 oder gibt ihn über die Umgebungsvariable PORT vor
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_webserver)
    t.start()

# --- BOT LOGIK ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class MeinBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Cogs laden
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Modul geladen: {filename}")
        
        await self.tree.sync()
        print("Slash-Commands synchronisiert.")

    async def on_ready(self):
        print(f'Eingeloggt als {self.user}')

bot = MeinBot()

if __name__ == '__main__':
    # Starte den Webserver
    keep_alive()
    
    # Starte den Bot
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("KEIN TOKEN GEFUNDEN!")