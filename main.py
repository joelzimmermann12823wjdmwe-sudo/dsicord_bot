import discord
from discord.ext import commands
import os
import traceback
import aiohttp
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
    return "🟢 Neon Bot System ist online und aktiv!"

def run_flask():
    """Startet den Webserver auf dem von Render zugewiesenen Port"""
    try:
        port = int(os.environ.get("PORT", 10000))
        # use_reloader=False ist extrem wichtig, damit Flask den Bot nicht doppelt startet!
        app.run(host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e:
        print(f"⚠️ Flask-Fehler: {e}")

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # help_command=None, da wir unser eigenes /help in der help.py machen
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = supabase 

    async def setup_hook(self):
        """Lädt automatisch alle Cogs aus dem /cogs Ordner"""
        cog_path = './cogs'
        if not os.path.exists(cog_path):
            os.makedirs(cog_path)
            print("📁 Ordner /cogs wurde erstellt.")
            
        # Lade alle .py Dateien im cogs Ordner
        for filename in os.listdir(cog_path):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Modul geladen: {filename}')
                except Exception as e:
                    print(f'❌ Fehler beim Laden von {filename}: {e}')

        # --- GLOBALER SLASH-COMMAND FEHLER-HANDLER ---
        # Dies behebt den Bug, dass Fehler bei / Commands nicht geloggt wurden
        self.tree.on_error = self.on_app_command_error

    async def on_ready(self):
        print(f"✅ ERFOLGREICH: {self.user} ist jetzt online!")
        if self.db:
            print("🗄️ Supabase-Datenbank verbunden.")
        
        try:
            # Synchronisiert die Slash-Commands mit Discord
            synced = await self.tree.sync()
            print(f"🔃 {len(synced)} Slash Commands synchronisiert.")
        except Exception as e:
            print(f"⚠️ Synchronisierungsfehler: {e}")

    async def send_error_webhook(self, error, command_name="Unbekannt", user_mention="Unbekannt"):
        """Hilfsfunktion: Sendet Fehler an den Discord Webhook"""
        webhook_url = os.getenv("ERROR_WEBHOOK_URL")
        admin_role_id = os.getenv("ADMIN_ROLE_ID")
        
        if not webhook_url:
            return

        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        short_tb = tb if len(tb) < 1000 else tb[:997] + "..."

        embed = discord.Embed(
            title="🚨 Neon Bot: System-Fehler",
            description="Ein kritischer Fehler wurde abgefangen.",
            color=0xff0000,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="📌 Befehl", value=f"`/{command_name}`", inline=True)
        embed.add_field(name="👤 User", value=user_mention, inline=True)
        embed.add_field(name="❌ Nachricht", value=f"```py\n{error}```", inline=False)
        embed.add_field(name="💻 Traceback", value=f"```py\n{short_tb}```", inline=False)
        
        embed.set_footer(text="Automatisches Monitoring")
        content = f"⚠️ <@&{admin_role_id}>" if admin_role_id else "⚠️ Systemfehler"

        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(webhook_url, session=session)
                await webhook.send(content=content, embed=embed, username="Neon Status")
        except Exception as e:
            print(f"❌ Webhook konnte nicht gesendet werden: {e}")

    # Handler für Prefix-Commands (!help etc)
    async def on_command_error(self, ctx, error):
        print(f"⚠️ Prefix-Fehler in {ctx.command}: {error}")
        await self.send_error_webhook(error, str(ctx.command), ctx.author.mention)

    # Handler für Slash-Commands (/help etc)
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        print(f"⚠️ Slash-Fehler in {interaction.command.name if interaction.command else 'Unbekannt'}: {error}")
        
        # Dem User eine freundliche Nachricht zeigen
        try:
            if interaction.response.is_done():
                await interaction.followup.send("❌ Es gab einen internen Fehler. Die Entwickler wurden informiert.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Es gab einen internen Fehler. Die Entwickler wurden informiert.", ephemeral=True)
        except:
            pass # Falls die Interaktion abgelaufen ist
            
        # Den Fehler an den Webhook senden
        await self.send_error_webhook(
            error, 
            interaction.command.name if interaction.command else "Unbekannt", 
            interaction.user.mention
        )

def start_bot():
    token = os.getenv("DISCORD_TOKEN")
    if not token or len(token) < 30:
        print("❌ KRITISCH: DISCORD_TOKEN fehlt oder ist ungültig!")
        return

    # Flask in einem separaten Daemon-Thread starten
    # Daemon bedeutet: Wenn der Bot stoppt, stoppt auch Flask sofort.
    t = Thread(target=run_flask, daemon=True)
    t.start()
    print("🌐 Keep-Alive Server gestartet.")

    bot = NeonBot()
    
    print("⏳ Versuche Verbindung zu Discord herzustellen...")
    try:
        # reconnect=True sorgt dafür, dass discord.py Verbindungsabbrüche (wie 429) selbst managt
        bot.run(token, reconnect=True)
    except discord.errors.HTTPException as e:
        print(f"❌ HTTP Fehler beim Start: {e}")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler beim Start: {e}")

if __name__ == "__main__":
    start_bot()