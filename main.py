import discord
from discord.ext import commands
from discord import app_commands
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

# --- 1. KONFIGURATION LADEN ---
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_KEY")
OWNER_ID = 1465263782258544680  # Deine ID

# --- 2. MINIMALER WEBSERVER (Für Render Keep-Alive) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "NEON BOT ist online! ⚡"

@app.route('/health')
def health():
    return "OK", 200

# --- 3. DIE BOT KLASSE ---
class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # Wir nutzen '!' als Präfix für Notfall-Befehle, primär aber Slash-Commands
        super().__init__(command_prefix="!", intents=intents)
        
        # Datenbank initialisieren
        self.db = None
        if SUPA_URL and SUPA_KEY and SyncPostgrestClient:
            try:
                self.db = SyncPostgrestClient(f"{SUPA_URL.strip()}/rest/v1", headers={
                    "apikey": SUPA_KEY.strip(), 
                    "Authorization": f"Bearer {SUPA_KEY.strip()}"
                })
                print("✅ Datenbank-Verbindung konfiguriert.")
            except Exception as e:
                print(f"❌ Datenbank-Initialisierungsfehler: {e}")

    async def setup_hook(self):
        """Wird aufgerufen, bevor der Bot sich mit Discord verbindet."""
        
        # --- GLOBALER INTERACTION CHECK (BAN-SYSTEM) ---
        async def global_interaction_check(interaction: discord.Interaction) -> bool:
            # Der Developer (Du) darf immer alles
            if interaction.user.id == OWNER_ID:
                return True

            if self.db:
                user_id = str(interaction.user.id)
                guild_id = str(interaction.guild_id) if interaction.guild else "0"

                try:
                    # Prüfen, ob User oder Server in der Ban-Tabelle stehen
                    res = self.db.table("bot_bans").select("target_id").in_("target_id", [user_id, guild_id]).execute()
                    
                    if res.data:
                        if not interaction.response.is_done():
                            await interaction.response.send_message(
                                "🚫 **Zugriff verweigert.** Du oder dieser Server wurde global von der Bot-Nutzung ausgeschlossen. Kontakt: https://neon-bot-2026.vercel.app/contact", 
                                ephemeral=True
                            )
                        return False # Blockiert den Command
                except Exception as e:
                    print(f"⚠️ Fehler beim Ban-Check: {e}")
            
            return True # Zugriff erlaubt

        # Den Check dem Slash-Command-System zuweisen
        self.tree.interaction_check = global_interaction_check

        # --- COGS AUTOMATISCH LADEN ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_path = os.path.join(base_dir, 'cogs')
        
        if os.path.exists(cogs_path):
            for filename in os.listdir(cogs_path):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"📦 Geladen: {filename}")
                    except Exception as e:
                        print(f"❌ Fehler beim Laden von {filename}: {e}")

        # --- SYNC ---
        await self.tree.sync()
        print("✅ Slash-Commands global synchronisiert.")

    async def on_ready(self):
        print(f"⚡ Eingeloggt als {self.user.name} (ID: {self.user.id})")
        
        # Verbindungstest für die Status-DM
        db_status = "❌ Nicht verbunden"
        if self.db:
            try:
                self.db.table("guild_settings").select("count", count="exact").limit(1).execute()
                db_status = "✅ Erfolgreich verbunden"
            except Exception as e:
                db_status = f"⚠️ Fehler: {e}"

        # Status-DM an dich senden
        try:
            owner = await self.fetch_user(OWNER_ID)
            if owner:
                embed = discord.Embed(
                    title="🚀 NEON BOT Status-Update",
                    description="Der Bot ist erfolgreich hochgefahren.",
                    color=discord.Color.from_rgb(0, 212, 255)
                )
                embed.add_field(name="Datenbank (Supabase)", value=db_status)
                embed.add_field(name="Globaler Check", value="🛡️ Aktiviert")
                embed.set_footer(text=f"Startzeit: {discord.utils.utcnow().strftime('%H:%M:%S')} UTC")
                await owner.send(embed=embed)
        except Exception as e:
            print(f"Konnte keine Start-DM senden: {e}")

    async def on_disconnect(self):
        print("🚨 Verbindung zu Discord verloren...")

# --- 4. START-LOGIK ---
bot = NeonBot()

def run_flask():
    # Port 10000 ist Standard für Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ KRITISCHER FEHLER: Kein DISCORD_TOKEN in der Umgebung gefunden!")
    else:
        # Flask Webserver in eigenem Thread (Keep-alive)
        Thread(target=run_flask, daemon=True).start()
        # Bot starten
        bot.run(TOKEN)