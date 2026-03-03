import discord
from discord import app_commands
from discord.ext import commands

class MUTE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Befehl: mute")
    async def mute(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /mute wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MUTE(bot))