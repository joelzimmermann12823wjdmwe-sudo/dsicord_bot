import discord
from discord import app_commands
from discord.ext import commands

class UPTIME(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="uptime", description="Befehl: uptime")
    
    async def uptime(self, interaction: discord.Interaction ):
        try:
            import time; await interaction.response.send_message(f'⏱️ Bot-Sitzung läuft stabil.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UPTIME(bot))