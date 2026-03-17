import discord
from discord.ext import commands
import os
import warnings
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Unterdrückt veraltete Warnungen
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Supabase Integration
try:
    from postgrest import SyncPostgrestClient
except ImportError:
    SyncPostgrestClient = None

# --- KONFIGURATION LADEN ---
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_KEY")
OWNER_ID = 1465263782258544680  # Deine ID bleibt fest

# --- MINIMALER WEBSERVER (Für Hosting-Provider wie Render) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "NEON BOT ist online! ⚡"

@app.route('/health')
def health():
    return "OK", 200

# --- NEON BOT KLASSE ---
class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # Datenbank-Client initialisieren
        self.db = None
        if SUPA_URL and SUPA_KEY and SyncPostgrestClient:
            try:
                self.db = SyncPostgrestClient(f"{SUPA_URL}/rest/v1", headers={
                    "apikey": SUPA_KEY, 
                    "Authorization": f"Bearer {SUPA_KEY}"
                })
                print("✅ Datenbank-Verbindung konfiguriert.")
            except Exception as e:
                print(f"❌ Datenbank-Fehler: {e}")

    async def setup_hook(self):
        # Cogs automatisch laden
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_path = os.path.join(base_dir, 'cogs')
        
        if os.path.exists(cogs_path):
            for filename in os.listdir(cogs_path):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"Geladen: {filename}")
                    except Exception as e:
                        print(f"❌ Fehler beim Laden von {filename}: {e}")

        # Slash Commands synchronisieren
        await self.tree.sync()
        print("✅ Slash-Commands global synchronisiert.")

    async def on_ready(self):
        print(f'⚡ {self.user.name} ist online und bereit!')
        
        # 1. Datenbank Verbindungstest
        db_status = "❌ Nicht verbunden"
        if self.db:
            try:
                self.db.table("guild_settings").select("count", count="exact").limit(1).execute()
                db_status = "✅ Erfolgreich verbunden"
            except Exception as e:
                db_status = f"❌ Fehler: {e}"

        # 2. Status-DM an dich senden
        try:
            owner = await self.fetch_user(OWNER_ID)
            if owner:
                embed = discord.Embed(
                    title="🚀 NEON BOT Status-Update",
                    description="Der Bot wurde gerade erfolgreich gestartet.",
                    color=discord.Color.from_rgb(0, 212, 255)
                )
                embed.add_field(name="Datenbank (Supabase)", value=db_status)
                embed.set_footer(text=f"Zeitpunkt: {discord.utils.utcnow().strftime('%H:%M:%S')} UTC")
                await owner.send(embed=embed)
        except Exception as e:
            print(f"Konnte keine Start-DM senden: {e}")

    async def on_disconnect(self):
        print("🚨 Die Verbindung zum Bot wurde unterbrochen!")

# Instanz erstellen
bot = NeonBot()

# --- START FUNKTIONEN ---
def run_flask():
    # Render nutzt meist Port 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ FEHLER: Kein DISCORD_TOKEN gefunden.")
    else:
        # Flask Webserver in einem eigenen Thread starten (Keep-alive)
        Thread(target=run_flask, daemon=True).start()
        # Bot starten
        bot.run(TOKEN)