import discord
from discord import app_commands
from discord.ext import commands
import sys

class owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="restart", description="Startet den Bot neu")
    async def restart(self, itx: discord.Interaction):
        # Ersetze die ID mit deiner Discord-ID!
        if itx.user.id != itx.client.application.owner.id:
            return await itx.response.send_message("❌ Zugriff verweigert.", ephemeral=True)
        
        await itx.response.send_message("🔄 Starte neu...", ephemeral=True)
        sys.exit()

async def setup(bot):
    await bot.add_cog(owner(bot))