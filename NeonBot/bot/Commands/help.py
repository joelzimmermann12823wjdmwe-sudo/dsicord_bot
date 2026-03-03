import discord
from discord import app_commands
from discord.ext import commands

class HELP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Befehl: help")
    
    async def help(self, interaction: discord.Interaction ):
        try:
            await interaction.response.send_message('💡 Tippe / um alle verfügbaren Befehle und ihre Funktionen zu sehen.', ephemeral=True)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(HELP(bot))