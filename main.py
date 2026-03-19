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

    # --- HILFSFUNKTION FÜR DEN BAN-CHECK ---
    async def check_is_banned(self, user_id: int, guild_id: int = None) -> bool:
        """Gibt True zurück, wenn der User oder der Server gebannt ist."""
        if user_id == OWNER_ID:
            return False
            
        if self.db:
            try:
                u_id = str(user_id)
                g_id = str(guild_id) if guild_id else "0"
                
                # Wir fragen gezielt ab
                res = self.db.table("bot_bans").select("target_id").in_("target_id", [u_id, g_id]).execute()
                return len(res.data) > 0
            except Exception as e:
                print(f"Check-Fehler: {e}")
        return False

    async def setup_hook(self):
        # 1. CHECK FÜR SLASH-COMMANDS
        async def global_interaction_check(interaction: discord.Interaction) -> bool:
            is_banned = await self.check_is_banned(interaction.user.id, interaction.guild_id)
            if is_banned:
                if not interaction.response.is_done():
                    await interaction.response.send_message("🚫 Dieser User/Server ist gesperrt.", ephemeral=True)
                return False
            return True

        self.tree.interaction_check = global_interaction_check

        # 2. CHECK FÜR PRÄFIX- & HYBRID-COMMANDS (WICHTIG!)
        @self.check
        async def global_command_check(ctx):
            is_banned = await self.check_is_banned(ctx.author.id, ctx.guild.id if ctx.guild else None)
            if is_banned:
                await ctx.send("🚫 Zugriff verweigert: Sperre aktiv.", delete_after=5)
                return False
            return True

        # Cogs laden
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_path = os.path.join(base_dir, 'cogs')
        if os.path.exists(cogs_path):
            for filename in os.listdir(cogs_path):
                if filename.endswith('.py'):
                    await self.load_extension(f'cogs.{filename[:-3]}')

        await self.tree.sync()

    async def on_ready(self):
        print(f"⚡ {self.user.name} bereit!")

bot = NeonBot()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if TOKEN:
        Thread(target=run_flask, daemon=True).start()
        bot.run(TOKEN)