import discord
from discord import app_commands
from discord.ext import commands

class SETLOGCHANNEL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setlogchannel", description="Befehl: setlogchannel")
    
    async def setlogchannel(self, interaction: discord.Interaction ):
        try:
            await interaction.response.send_message(f'✅ System-Modul für setlogchannel wurde initialisiert.', ephemeral=True)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SETLOGCHANNEL(bot))