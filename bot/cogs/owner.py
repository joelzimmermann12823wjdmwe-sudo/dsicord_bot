import discord
from discord import app_commands
from discord.ext import commands
import sys
import os

class owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="restart", description="Startet den Bot neu (Nur für Bot-Besitzer)")
    async def restart(self, itx: discord.Interaction):
        # Prüfen, ob der User der App-Besitzer ist
        if itx.user.id != itx.client.application.owner.id:
            return await itx.response.send_message("❌ Nur der Bot-Besitzer kann diesen Command nutzen!", ephemeral=True)
        
        await itx.response.send_message("🔄 Bot wird neu gestartet... Bitte warten.", ephemeral=True)
        print("Reboot wird durch Command ausgelöst...")
        
        # Beendet den Prozess. Render startet ihn automatisch neu.
        sys.exit()

async def setup(bot):
    await bot.add_cog(owner(bot))