import discord
from discord.ext import commands
import os
import traceback
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask
from threading import Thread

# Variablen laden
load_dotenv()

# --- SUPABASE SETUP ---
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
# Initialisierung nur, wenn die Daten vorhanden sind
supabase: Client = create_client(url, key) if url and key else None

# --- FLASK SERVER (Keep-Alive für Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Neon Bot ist online!"

def run_flask():
    # Render nutzt meist Port 10000
    app.run(host='0.0.0.0', port=10000)

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = supabase # Datenbank-Zugriff in Cogs über self.bot.db

    async def setup_hook(self):
        cog_path = './cogs'
        if not os.path.exists(cog_path):
            os.makedirs(cog_path)
            
        for filename in os.listdir(cog_path):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Modul geladen: {filename}')
                except Exception as e:
                    print(f'❌ Fehler beim Laden von {filename}: {e}')

    async def on_ready(self):
        print(f'🚀 Hauptbot eingeloggt als {self.user}')
        if self.db:
            print("🗄️ Verbindung zu Supabase steht.")
        else:
            print("⚠️ Supabase nicht verbunden (Keys fehlen in .env).")
        await self.tree.sync()

    async def on_command_error(self, ctx, error):
        log_id = os.getenv("LOG_CHANNEL_ID")
        if log_id:
            channel = self.get_channel(int(log_id))
            if channel:
                tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                report = f"[ERROR_REPORT]|{ctx.command}|{ctx.author.id}|{error}|{tb[:1000]}"
                await channel.send(report)

if __name__ == "__main__":
    # Flask in einem eigenen Thread starten
    Thread(target=run_flask).start()
    
    bot = NeonBot()
    bot.run(os.getenv("DISCORD_TOKEN"))