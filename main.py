import discord
from discord.ext import commands
from discord import app_commands
import os
import warnings
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=DeprecationWarning) 

try:
    from postgrest import SyncPostgrestClient
except ImportError:
    SyncPostgrestClient = None

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_KEY")
OWNER_ID = 1465263782258544680 

app = Flask(__name__)

@app.route('/')
def home():
    return "NEON BOT ist online! ⚡"

# --- DIE BOT KLASSE ---
class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        self.db = None
        if SUPA_URL and SUPA_KEY and SyncPostgrestClient:
            try:
                self.db = SyncPostgrestClient(f"{SUPA_URL.strip()}/rest/v1", headers={
                    "apikey": SUPA_KEY.strip(), 
                    "Authorization": f"Bearer {SUPA_KEY.strip()}"
                })
            except Exception as e:
                print(f"❌ DB-Fehler: {e}")

    # --- DAS HERZSTÜCK DES BAN-SYSTEMS ---
    async def is_banned(self, user_id: int, guild_id: int) -> bool:
        """Prüft blitzschnell, ob eine ID in der Supabase-Datenbank steht."""
        if user_id == OWNER_ID:
            return False # Du darfst immer alles
            
        if self.db:
            try:
                u_id = str(user_id)
                g_id = str(guild_id) if guild_id else "0"
                res = self.db.table("bot_bans").select("target_id").in_("target_id", [u_id, g_id]).execute()
                return len(res.data) > 0
            except:
                pass # Falls Supabase mal 1 Sekunde laggt, stürzt der Bot nicht ab
        return False

    # --- 1. SCHUTZ FÜR NORMALE TEXT-BEFEHLE (!befehl) ---
    async def bot_check(self, ctx):
        if await self.is_banned(ctx.author.id, ctx.guild.id if ctx.guild else None):
            # Wenn es ein Präfix-Command ist, senden wir eine Nachricht
            if ctx.interaction is None:
                await ctx.send("🚫 **Zugriff verweigert:** Du oder dieser Server ist von der Bot-Nutzung ausgeschlossen.", delete_after=5)
            # Dieser Fehler blockt die Ausführung und wird vom Error-Handler unten leise abgefangen
            raise commands.CheckFailure("Banned user/server attempted to use a command.")
        return True

    async def setup_hook(self):
        # --- 2. SCHUTZ FÜR SLASH-BEFEHLE (/befehl) ---
        async def global_interaction_check(interaction: discord.Interaction) -> bool:
            if await self.is_banned(interaction.user.id, interaction.guild_id):
                if not interaction.response.is_done():
                    await interaction.response.send_message("🚫 **Zugriff verweigert:** Dieser User/Server ist gesperrt.", ephemeral=True)
                return False
            return True

        self.tree.interaction_check = global_interaction_check

        # Wir binden den eigenen Error-Handler ein, um die Konsole sauber zu halten
        self.tree.on_error = self.on_tree_error

        # Cogs laden
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_path = os.path.join(base_dir, 'cogs')
        if os.path.exists(cogs_path):
            for filename in os.listdir(cogs_path):
                if filename.endswith('.py'):
                    await self.load_extension(f'cogs.{filename[:-3]}')

        await self.tree.sync()

    # --- ERROR-HANDLER: KONSOLE SAUBER HALTEN ---
    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # Ignoriert den "CheckFailure"-Fehler, der entsteht, wenn wir einen gesperrten User blocken
        if isinstance(error, app_commands.CheckFailure):
            pass 
        else:
            print(f"⚠️ Slash-Command Fehler: {error}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass 
        elif isinstance(error, commands.CommandNotFound):
            pass # Ignoriert Fehler, wenn jemand z.B. "!gibtsnicht" tippt
        else:
            print(f"⚠️ Text-Command Fehler: {error}")

    async def on_ready(self):
        print(f"⚡ {self.user.name} ist online und komplett geschützt!")

bot = NeonBot()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if TOKEN:
        Thread(target=run_flask, daemon=True).start()
        bot.run(TOKEN)