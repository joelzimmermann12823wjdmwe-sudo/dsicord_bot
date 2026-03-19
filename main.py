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

# --- 2. MINIMALER WEBSERVER (Für Hosting-Provider wie Render) ---
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
        # WICHTIG: help_command=None erlaubt deine eigene cogs/help.py
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            help_command=None 
        )
        
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

    # --- BAN-CHECK LOGIK (DAS GEDÄCHTNIS) ---
    async def is_banned(self, user_id: int, guild_id: int = None) -> bool:
        """Prüft, ob User oder Server in der Datenbank gesperrt sind."""
        if user_id == OWNER_ID:
            return False # Du wirst niemals gesperrt

        if self.db:
            try:
                u_id = str(user_id)
                g_id = str(guild_id) if guild_id else "0"
                # Suche nach Treffern in der Ban-Tabelle
                res = self.db.table("bot_bans").select("target_id").in_("target_id", [u_id, g_id]).execute()
                return len(res.data) > 0
            except:
                return False # Im Zweifel (DB-Lag) Zugriff gewähren
        return False

    # --- 1. SCHUTZ FÜR TEXT-BEFEHLE (!) ---
    async def bot_check(self, ctx):
        banned = await self.is_banned(ctx.author.id, ctx.guild.id if ctx.guild else None)
        if banned:
            # Nur bei echten Textnachrichten (nicht Slash) antworten
            if ctx.interaction is None:
                await ctx.send("🚫 **Zugriff verweigert:** Sperre aktiv.", delete_after=5)
            raise commands.CheckFailure("Banned")
        return True

    async def setup_hook(self):
        """Wird vor dem Bot-Start ausgeführt."""

        # --- 2. SCHUTZ FÜR SLASH-BEFEHLE (/) ---
        async def global_interaction_check(interaction: discord.Interaction) -> bool:
            banned = await self.is_banned(interaction.user.id, interaction.guild_id)
            if banned:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "🚫 **Zugriff verweigert:** Du oder dieser Server wurde global gesperrt.", 
                        ephemeral=True
                    )
                return False
            return True

        # Check dem Slash-System zuweisen
        self.tree.interaction_check = global_interaction_check
        # Eigenen Error-Handler für Slash-Commands binden
        self.tree.on_error = self.on_tree_error

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

        # Synchronisierung
        await self.tree.sync()
        print("✅ Slash-Commands global synchronisiert.")

    # --- ERROR HANDLING (Hält die Konsole sauber) ---
    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            pass # Stummes Ignorieren von Bans in der Konsole
        else:
            print(f"⚠️ Slash-Error: {error}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass # Stummes Ignorieren von Bans
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(f"⚠️ Prefix-Error: {error}")

    async def on_ready(self):
        print(f"⚡ {self.user.name} ist online und bereit!")

# --- 4. START-LOGIK ---
bot = NeonBot()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ KRITISCHER FEHLER: Kein DISCORD_TOKEN gefunden!")
    else:
        # Flask Webserver in eigenem Thread starten
        Thread(target=run_flask, daemon=True).start()
        # Bot starten
        bot.run(TOKEN)