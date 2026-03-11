import discord
from discord.ext import commands
import os
import datetime
from dotenv import load_dotenv

# Variablen laden (.env oder Render Environment)
load_dotenv()

# --- KONFIGURATION (Direkt im Code) ---
LOG_CHANNEL_ID = 1480922888445100201  # Hier die ID deines Log-Kanals einfügen
ADMIN_ROLE_ID = 1481351901994942555   # Hier die ID deiner Admin-Rolle einfügen

class StatusBot(commands.Bot):
    def __init__(self):
        # Der Status Bot benötigt alle Intents, um Nachrichten lesen und löschen zu können
        intents = discord.Intents.all()
        super().__init__(command_prefix="s!", intents=intents)
        self.error_counter = 0

    async def on_ready(self):
        print(f"✅ Status-Wächter aktiv: {self.user}")
        # Zeigt in der Mitgliederliste an, dass er den Hauptbot überwacht
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="Neon Bot Fehler"
            )
        )

    async def on_message(self, message):
        # Ignoriere Nachrichten von sich selbst
        if message.author.id == self.user.id:
            return

        # Sicherstellen, dass der Bot nur im richtigen Kanal auf Error-Reports achtet
        if message.channel.id != LOG_CHANNEL_ID:
            return

        # Erkennt Berichte vom Hauptbot anhand des Präfix [ERROR_REPORT]
        if message.content.startswith("[ERROR_REPORT]"):
            self.error_counter += 1
            
            try:
                # Daten zerlegen (Format: [ERROR_REPORT]|Command|UserID|Error|Traceback)
                parts = message.content.split("|")
                
                # Sicherheitscheck, falls die Nachricht nicht das richtige Format hat
                if len(parts) < 5:
                    return

                cmd_name = parts[1]
                user_id = parts[2]
                err_msg = parts[3]
                tb_msg = parts[4]
                
                # 1. Die Roh-Nachricht vom Hauptbot sofort löschen
                try:
                    await message.delete()
                except discord.Forbidden:
                    print("❌ Fehler: Der Status-Bot hat keine Rechte, Nachrichten zu löschen!")

                # 2. Das professionelle Alarm-Embed erstellen
                embed = discord.Embed(
                    title="🚨 Neon Bot: System-Fehler",
                    description="Ein kritischer Fehler wurde im Hauptbot abgefangen.",
                    color=0xff0000, # Rot für Alarm
                    timestamp=datetime.datetime.utcnow()
                )
                
                embed.add_field(name="📌 Befehl", value=f"`/{cmd_name}`", inline=True)
                embed.add_field(name="🔢 Fehler-Nr.", value=f"#{self.error_counter}", inline=True)
                embed.add_field(name="👤 Verursacher", value=f"<@{user_id}>", inline=True)
                
                # Fehlermeldung und Traceback (Code-Ebene)
                embed.add_field(name="❌ Fehlermeldung", value=f"```py\n{err_msg}```", inline=False)
                
                # Traceback kürzen, falls er zu lang für ein Embed Feld ist (Limit 1024)
                short_tb = tb_msg if len(tb_msg) < 1000 else tb_msg[:997] + "..."
                embed.add_field(name="💻 Code-Ebene (Traceback)", value=f"```py\n{short_tb}```", inline=False)
                
                embed.set_footer(text="Status: Wartet auf Fehlerbehebung")

                # 3. Admin-Rolle pingen
                ping_content = f"⚠️ <@&{ADMIN_ROLE_ID}> Ein neuer Fehler wurde protokolliert!"
                
                # Nachricht senden
                await message.channel.send(content=ping_content, embed=embed)
                
            except Exception as e:
                print(f"❌ Fehler beim Verarbeiten des Error-Reports: {e}")

# Bot mit dem STATUS_TOKEN aus der .env / Render starten
if __name__ == "__main__":
    token = os.getenv("STATUS_TOKEN")
    if token:
        bot = StatusBot()
        bot.run(token)
    else:
        print("❌ STATUS_TOKEN wurde nicht in den Umgebungsvariablen gefunden!")