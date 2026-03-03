import discord
from discord import app_commands
from discord.ext import commands

class TESTWELCOME(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="testwelcome", description="Befehl: testwelcome")
    
    async def testwelcome(self, interaction: discord.Interaction ):
        try:
            await interaction.response.send_message(f'✅ System-Modul für testwelcome wurde initialisiert.', ephemeral=True)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TESTWELCOME(bot))