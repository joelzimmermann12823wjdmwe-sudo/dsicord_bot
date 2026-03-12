import discord
from discord.ext import commands, tasks
import os
import traceback
import aiohttp
import asyncio
import datetime
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
    return "🟢 Neon Bot System ist online und aktiv!"

def run_flask():
    """Startet den Webserver auf dem von Render zugewiesenen Port"""
    try:
        port = int(os.environ.get("PORT", 10000))
        app.run(host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e:
        print(f"⚠️ Flask-Fehler: {e}")

class NeonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = supabase 
        self.active_incidents = {} # {incident_type: {msg_id, start_time, last_status, channel_id}}

    async def setup_hook(self):
        """Lädt Cogs und startet den Monitor-Task"""
        # Cogs laden
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

        # Slash-Command Fehler-Handler
        self.tree.on_error = self.on_app_command_error
        
        # Status-Monitor Task starten
        self.monitor_systems.start()

    @tasks.loop(seconds=2.0)
    async def monitor_systems(self):
        """Überprüft alle 2 Sekunden die Vitalwerte der Systeme."""
        channel_id = os.getenv("ERROR_CHANNEL_ID")
        if not channel_id:
            return

        # 1. Check Discord API & Latency
        try:
            latency = self.latency * 1000
            api_status = "stable" if latency < 250 else "unstable"
            if latency > 1000 or latency == 0: api_status = "down"
        except:
            api_status = "down"

        # 2. Check Database Connection (Supabase)
        db_status = "stable"
        if self.db:
            try:
                # Schneller Test-Query ohne große Last
                self.db.table("pings").select("*").limit(1).execute()
            except:
                db_status = "down"
        else:
            db_status = "down"

        # System-Status Management
        await self.manage_incident("Discord API", api_status, channel_id)
        await self.manage_incident("Datenbank", db_status, channel_id)

    async def manage_incident(self, system_name, current_status, channel_id):
        """Verwaltet die Embeds basierend auf dem Status (Rot, Orange, Grün)."""
        incident_key = system_name
        data = self.active_incidents.get(incident_key)
        
        if current_status == "stable" and not data:
            return

        channel = self.get_channel(int(channel_id))
        if not channel:
            return

        now = datetime.datetime.now()

        # FALL 1: System DOWN (ROT)
        if current_status == "down" and (not data or data['last_status'] != "down"):
            embed = discord.Embed(
                title="🔴 Kritischer Fehler",
                description=f"**System:** `{system_name}`\n"
                            f"❗ `[{now.strftime('%H:%M:%S')}]` **Status: Problem erkannt**\n"
                            f"Es wurde eine schwere Störung im Modul `{system_name}` festgestellt. Der Betrieb ist aktuell unterbrochen.\n\n"
                            f"🚫 **Priorität:** Hoch",
                color=0xf04747
            )
            await self._update_or_send_incident(incident_key, embed, "down", channel, now)

        # FALL 2: System INSTABIL (ORANGE)
        elif current_status == "unstable" and (not data or data['last_status'] != "unstable"):
            embed = discord.Embed(
                title="🟠 In Bearbeitung",
                description=f"**System:** `{system_name}`\n"
                            f"⏳ `[{now.strftime('%H:%M:%S')}]` **Status: Analyse**\n"
                            f"Das System `{system_name}` zeigt Verzögerungen. Die automatische Fehlerbehebung wurde eingeleitet.\n\n"
                            f"⚙️ **Status:** Techniker/System-Skripte arbeiten...",
                color=0xfaa61a
            )
            await self._update_or_send_incident(incident_key, embed, "unstable", channel, now)

        # FALL 3: System STABIL (GRÜN)
        elif current_status == "stable" and data:
            start_time = data['start_time']
            duration = now - start_time
            duration_str = f"{int(duration.total_seconds() // 60)}m {int(duration.total_seconds() % 60)}s"

            embed = discord.Embed(
                title="🟢 Alles funktioniert wieder",
                description=f"**System:** `{system_name}`\n"
                            f"✅ `[{now.strftime('%H:%M:%S')}]` **Status: Behoben**\n"
                            f"Die Störung im Bereich `{system_name}` wurde erfolgreich identifiziert und korrigiert.\n\n"
                            f"⏱️ **Ausfallzeit:** {duration_str}",
                color=0x43b581
            )
            try:
                msg = await channel.fetch_message(data['msg_id'])
                await msg.edit(embed=embed)
            except: pass
            del self.active_incidents[incident_key]

    async def _update_or_send_incident(self, key, embed, status, channel, time_now):
        """Hilfsfunktion zum Senden oder Editieren von Incident-Nachrichten"""
        data = self.active_incidents.get(key)
        if data:
            try:
                msg = await channel.fetch_message(data['msg_id'])
                await msg.edit(embed=embed)
                self.active_incidents[key].update({'last_status': status})
            except:
                msg = await channel.send(embed=embed)
                self.active_incidents[key].update({'msg_id': msg.id, 'last_status': status})
        else:
            msg = await channel.send(embed=embed)
            self.active_incidents[key] = {
                'msg_id': msg.id, 'start_time': time_now, 'last_status': status, 
                'channel_id': str(channel.id)
            }

    async def on_ready(self):
        print(f"✅ ERFOLGREICH: {self.user} ist online!")
        await self.tree.sync()

    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Meldet Command-Fehler sofort als Incident (Rot)"""
        cmd_name = f"Command: {interaction.command.name}" if interaction.command else "Allgemeine API"
        channel_id = os.getenv("ERROR_CHANNEL_ID")
        if channel_id:
            await self.manage_incident(cmd_name, "down", channel_id)
        
        # Internes Error-Logging via Webhook bleibt als Backup
        await self.send_error_webhook(error, cmd_name, interaction.user.mention)

    async def send_error_webhook(self, error, command_name, user_mention):
        webhook_url = os.getenv("ERROR_WEBHOOK_URL")
        if not webhook_url: return
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            embed = discord.Embed(title="🚨 Interner Traceback", description=f"```py\n{error}```", color=0xff0000)
            await webhook.send(embed=embed, username="Neon Debugger")

def start_bot():
    token = os.getenv("DISCORD_TOKEN")
    if not token: return
    t = Thread(target=run_flask, daemon=True)
    t.start()
    bot = NeonBot()
    bot.run(token, reconnect=True)

if __name__ == "__main__":
    start_bot()