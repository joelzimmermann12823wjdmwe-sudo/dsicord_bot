import discord
from discord import app_commands
from discord.ext import commands

class TEMPBAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tempban", description="Befehl: tempban")
    async def tempban(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /tempban wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TEMPBAN(bot))