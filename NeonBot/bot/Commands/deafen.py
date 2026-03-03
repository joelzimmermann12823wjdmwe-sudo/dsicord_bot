import discord
from discord import app_commands
from discord.ext import commands

class DEAFEN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="deafen", description="Befehl: deafen")
    async def deafen(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /deafen wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DEAFEN(bot))