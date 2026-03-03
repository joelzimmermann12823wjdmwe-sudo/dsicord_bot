import discord
from discord.ext import commands
import os
import sys
from aiohttp import web
import asyncio

# Fügt das Hauptverzeichnis zum Systempfad hinzu, damit Render die Modul-Struktur erkennt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class NeonBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", 
            intents=discord.Intents.all(), 
            help_command=None
        )

    async def setup_hook(self):
        """Wird beim Starten ausgeführt, um alle 50+ Module zu laden."""
        print("🚀 Starte Modul-Loader für 50+ Commands...")
        
        # Pfad zum Commands-Ordner (relativ zur main.py)
        commands_path = os.path.join(os.path.dirname(__file__), 'Commands')
        
        if os.path.exists(commands_path):
            for filename in os.listdir(commands_path):
                # Lade jede .py Datei, die nicht mit __ beginnt (wie __init__.py)
                if filename.endswith(".py") and not filename.startswith("__"):
                    extension = f"bot.Commands.{filename[:-3]}"
                    try:
                        await self.load_extension(extension)
                        print(f"✅ Modul geladen: {filename}")
                    except Exception as e:
                        print(f"❌ Fehler beim Laden von {filename}: {e}")
        else:
            print(f"⚠️ Warnung: Ordner {commands_path} wurde nicht gefunden!")

        # Startet den Hintergrund-Webserver für Render (Port-Binding Fix)
        self.loop.create_task(self.start_renderer_webserver())
        print("--- NeonBot Setup abgeschlossen ---")

    async def start_renderer_webserver(self):
        """Erstellt einen kleinen Webserver, um Render 'Live' zu signalisieren."""
        async def handle(request):
            return web.Response(text="NeonBot is Online and Healthy!")

        app = web.Application()
        app.router.add_get('/', handle)
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Nutzt den von Render vergebenen Port oder Standard 10000
        port = int(os.getenv("PORT", 10000))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f"🌍 Webserver aktiv auf Port {port}")

# Bot Instanz erstellen
bot = NeonBot()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Befehl zum manuellen Synchronisieren der Slash-Commands: !sync"""
    await ctx.send("⏳ Synchronisiere 50+ Slash-Commands mit Discord... Bitte warten.")
    try:
        # Registriert alle geladenen Commands global bei der Discord API
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Erfolg! {len(synced)} Slash-Commands sind jetzt online.")
        print(f"Globaler Sync durchgeführt: {len(synced)} Commands.")
    except Exception as e:
        await ctx.send(f"❌ Synchronisationsfehler: {e}")
        print(f"Sync-Fehler: {e}")

# Bot starten
if __name__ == "__main__":
    token = os.getenv('TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ FEHLER: Kein TOKEN in den Umgebungsvariablen gefunden!")