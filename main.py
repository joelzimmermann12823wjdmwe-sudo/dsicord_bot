import discord
from discord.ext import commands
import os
import traceback
import aiohttp
import asyncio
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask
from threading import Thread

# Umgebungsvariablen laden
load_dotenv()

# --- SUPABASE SETUP ---
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key) if url and key else None

# --- FLASK SERVER (Keep-Alive für Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Neon Bot ist online und aktiv!"

def run_flask():
    # Render nutzt Port 10000
    try:
        app.run(host='0.0.0.0', port=10000)
    except Exception as e:
        print(f"⚠️ Flask-Server Fehler: {e}")

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = supabase 

    async def setup_hook(self):
        """Lädt automatisch alle Cogs aus dem /cogs Ordner"""
        cog_path = './cogs'
        if not os.path.exists(cog_path):
            os.makedirs(cog_path)
            print("📁 Ordner /cogs wurde erstellt.")
            
        for filename in os.listdir(cog_path):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Cog geladen: {filename}')
                except Exception as e:
                    print(f'❌ Fehler beim Laden von {filename}: {e}')

    async def on_ready(self):
        print(f'🚀 ERFOLGREICH: Eingeloggt als {self.user} (ID: {self.user.id})')
        if self.db:
            print("🗄️ Supabase-Datenbank verbunden.")
        await self.tree.sync()
        print("🔃 Slash Commands synchronisiert.")

    async def on_command_error(self, ctx, error):
        """Status-Monitor: Sendet Fehlerberichte via Webhook"""
        webhook_url = os.getenv("ERROR_WEBHOOK_URL")
        admin_role_id = os.getenv("ADMIN_ROLE_ID")
        
        print(f"⚠️ Fehler in Befehl {ctx.command}: {error}")

        if not webhook_url:
            return

        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        short_tb = tb if len(tb) < 1000 else tb[:997] + "..."

        embed = discord.Embed(
            title="🚨 Neon Bot: System-Fehler",
            description="Ein Fehler ist während der Ausführung eines Befehls aufgetreten.",
            color=0xff0000,
            timestamp=discord.utils.utcnow()
        )
        
        cmd_name = f"/{ctx.command}" if ctx.command else "Unbekannt"
        embed.add_field(name="📌 Befehl", value=f"`{cmd_name}`", inline=True)
        embed.add_field(name="👤 User", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
        embed.add_field(name="❌ Nachricht", value=f"```py\n{error}```", inline=False)
        embed.add_field(name="💻 Traceback", value=f"```py\n{short_tb}```", inline=False)
        
        embed.set_footer(text="Automatisches Log-System")
        content = f"⚠️ <@&{admin_role_id}> Ein Fehler wurde gemeldet!" if admin_role_id else "⚠️ Ein Fehler wurde gemeldet!"

        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(webhook_url, session=session)
                await webhook.send(content=content, embed=embed, username="Neon Status Wächter")
        except Exception as e:
            print(f"❌ Webhook-Fehler: {e}")

async def start_bot_logic():
    # Flask in einem Hintergrund-Thread starten, damit Render "Live" sieht
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Flask-Webserver für Render gestartet.")
    
    bot = NeonBot()
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print("❌ KRITISCH: Kein DISCORD_TOKEN in der .env gefunden!")
        return

    max_retries = 20
    retry_delay = 60 

    for attempt in range(max_retries):
        try:
            print(f"⏳ Verbindungsversuch {attempt+1} zu Discord...")
            await bot.start(token)
            break 
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print(f"⚠️ Cloudflare Rate Limit (429). Discord blockiert Render aktuell. Warte {retry_delay}s vor Neustart...")
                # Wir schließen den Bot-Client sauber vor dem Retry
                await bot.close()
                await asyncio.sleep(retry_delay)
            else:
                print(f"❌ HTTP Fehler {e.status}: {e}")
                break
        except Exception as e:
            print(f"❌ Unerwarteter Fehler beim Start: {e}")
            break

if __name__ == "__main__":
    try:
        asyncio.run(start_bot_logic())
    except KeyboardInterrupt:
        print("Bot manuell gestoppt.")