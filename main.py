import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from supabase import create_client, Client

# Webserver für Render
app = Flask('')
@app.route('/')
def home(): return "Neon Bot ist online!"

def run_webserver():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_webserver).start()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_KEY")

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        # Supabase Client initialisieren
        self.supabase: Client = create_client(SUPA_URL, SUPA_KEY)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        await self.tree.sync()
        print("✅ Befehle synchronisiert & Supabase verbunden.")

    async def on_ready(self):
        print(f'--- {self.user.name} ist bereit ---')

bot = NeonBot()

if __name__ == '__main__':
    keep_alive()
    bot.run(TOKEN)
