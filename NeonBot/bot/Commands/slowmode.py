import discord
from discord import app_commands
from discord.ext import commands

class SLOWMODE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="Befehl: slowmode")
    async def slowmode(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /slowmode wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SLOWMODE(bot))