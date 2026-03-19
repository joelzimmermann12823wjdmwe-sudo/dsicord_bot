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

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        
        self.db = None
        if SUPA_URL and SUPA_KEY and SyncPostgrestClient:
            try:
                self.db = SyncPostgrestClient(f"{SUPA_URL.strip()}/rest/v1", headers={
                    "apikey": SUPA_KEY.strip(), 
                    "Authorization": f"Bearer {SUPA_KEY.strip()}"
                })
                print("✅ Datenbank-Verbindung konfiguriert.")
            except Exception as e:
                print(f"❌ Datenbank-Fehler: {e}")

    # --- BAN-LOGIK: DATEN LÖSCHEN & VERLASSEN ---
    async def enforce_guild_ban(self, guild):
        """Kickt den Bot vom Server, löscht Daten und informiert den Owner."""
        if not guild: return

        # 1. Server Owner informieren
        try:
            contact_url = "https://neon-bot-2026.vercel.app/contact"
            embed = discord.Embed(
                title="🚫 Server dauerhaft gesperrt",
                description=(
                    f"Der Server **{guild.name}** ist global für diesen Bot gesperrt.\n"
                    "Einladungen werden automatisch abgelehnt und Daten wurden bereinigt.\n\n"
                    f"**Support & Einspruch:** [Kontaktformular]({contact_url})"
                ),
                color=discord.Color.from_rgb(255, 0, 0)
            )
            await guild.owner.send(embed=embed)
        except:
            pass # Falls DMs beim Owner zu sind

        # 2. Daten in Supabase löschen
        if self.db:
            try:
                g_id = str(guild.id)
                # Tabellen hier anpassen:
                tables = ["guild_settings", "warns", "economy", "welcome_messages"]
                for table in tables:
                    self.db.table(table).delete().eq("guild_id", g_id).execute()
                print(f"🧹 Daten für {guild.id} bereinigt.")
            except Exception as e:
                print(f"Löschfehler: {e}")

        # 3. Server sofort verlassen
        await guild.leave()
        print(f"🚪 Gebannten Server {guild.id} automatisch verlassen.")

    # --- EVENT: BEITRITT ZU EINEM NEUEN SERVER ---
    async def on_guild_join(self, guild):
        """Wird aufgerufen, wenn der Bot frisch auf einen Server eingeladen wird."""
        if self.db:
            try:
                res = self.db.table("bot_bans").select("target_id").eq("target_id", str(guild.id)).execute()
                if res.data:
                    await self.enforce_guild_ban(guild)
            except Exception as e:
                print(f"Fehler bei Beitritts-Prüfung: {e}")

    async def is_banned(self, user_id: int, guild_id: int = None) -> bool:
        """Prüft Bans bei Befehlsausführung."""
        if user_id == OWNER_ID: return False
        if self.db:
            try:
                u_id = str(user_id)
                g_id = str(guild_id) if guild_id else "0"
                res = self.db.table("bot_bans").select("target_id").in_("target_id", [u_id, g_id]).execute()
                
                # Falls der Server gebannt ist (während der Bot schon drauf ist)
                if any(str(item['target_id']) == g_id for item in res.data):
                    guild = self.get_guild(guild_id)
                    if guild:
                        await self.enforce_guild_ban(guild)
                    return True
                
                return len(res.data) > 0
            except:
                return False
        return False

    async def bot_check(self, ctx):
        if await self.is_banned(ctx.author.id, ctx.guild.id if ctx.guild else None):
            raise commands.CheckFailure("Banned")
        return True

    async def setup_hook(self):
        async def global_interaction_check(interaction: discord.Interaction) -> bool:
            if await self.is_banned(interaction.user.id, interaction.guild_id):
                return False
            return True

        self.tree.interaction_check = global_interaction_check
        self.tree.on_error = self.on_tree_error

        # Cogs laden
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cogs_path = os.path.join(base_dir, 'cogs')
        if os.path.exists(cogs_path):
            for filename in os.listdir(cogs_path):
                if filename.endswith('.py'):
                    await self.load_extension(f'cogs.{filename[:-3]}')

        await self.tree.sync()

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure): pass
        else: print(f"⚠️ Slash-Error: {error}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure): pass
        else: print(f"⚠️ Prefix-Error: {error}")

    async def on_ready(self):
        print(f"⚡ {self.user.name} online. Einlass-Sperre für gebannte Server ist AKTIV.")

bot = NeonBot()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if TOKEN:
        Thread(target=run_flask, daemon=True).start()
        bot.run(TOKEN)