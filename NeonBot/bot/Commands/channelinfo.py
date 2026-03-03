import discord
from discord import app_commands
from discord.ext import commands

class CHANNELINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="channelinfo", description="Befehl: channelinfo")
    
    async def channelinfo(self, interaction: discord.Interaction ):
        try:
            await interaction.response.send_message(f'✅ System-Modul für channelinfo wurde initialisiert.', ephemeral=True)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CHANNELINFO(bot))