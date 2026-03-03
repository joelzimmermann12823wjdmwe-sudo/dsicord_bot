import discord
from discord import app_commands
from discord.ext import commands

class VCKICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vckick", description="Befehl: vckick")
    async def vckick(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /vckick wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VCKICK(bot))