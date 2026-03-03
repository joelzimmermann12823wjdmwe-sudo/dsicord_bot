import discord
from discord import app_commands
from discord.ext import commands

class UNBANALL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unbanall", description="Befehl: unbanall")
    async def unbanall(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /unbanall wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNBANALL(bot))