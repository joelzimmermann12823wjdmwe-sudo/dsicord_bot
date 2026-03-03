import discord
from discord import app_commands
from discord.ext import commands

class PING(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Befehl: ping")
    
    async def ping(self, interaction: discord.Interaction ):
        try:
            await interaction.response.send_message(f'🏓 Latenz: {round(self.bot.latency * 1000)}ms')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PING(bot))