import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Lade Umgebungsvariablen (.env)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot-Klasse definieren
class NeonBot(commands.Bot):
    def __init__(self):
        # Definiert die Intents (Berechtigungen für Ereignisse)
        intents = discord.Intents.default()
        intents.message_content = True  # Wichtig für AutoMod & Prefix-Commands
        intents.members = True          # Wichtig für Welcome & Member-Logs
        
        super().__init__(
            command_prefix="!", 
            intents=intents,
            help_command=None # Wir nutzen unseren eigenen /help Command
        )

    async def setup_hook(self):
        """Wird aufgerufen, bevor der Bot online geht."""
        print("--- Lade Cogs aus dem Ordner 'cogs' ---")
        
        # Gehe durch alle Dateien im Ordner 'cogs'
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        # Lädt jede .py Datei als Extension
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f'✅ Erfolgreich geladen: {filename}')
                    except Exception as e:
                        print(f'❌ Fehler beim Laden von {filename}: {e}')
        else:
            print("⚠️ Ordner 'cogs' wurde nicht gefunden!")

        # Synchronisiert die Slash-Commands mit Discord
        print("--- Synchronisiere Slash-Commands ---")
        try:
            synced = await self.tree.sync()
            print(f"✅ {len(synced)} Slash-Commands erfolgreich synchronisiert.")
        except Exception as e:
            print(f"❌ Fehler beim Synchronisieren: {e}")

    async def on_ready(self):
        """Wird aufgerufen, wenn der Bot eingeloggt ist."""
        print(f"--- {self.user.name} ist jetzt online! ---")
        print(f"ID: {self.user.id}")
        
        # Status setzen
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="auf deine Commands | /help"
            )
        )

# Bot-Instanz erstellen und starten
async def main():
    bot = NeonBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot wird beendet...")