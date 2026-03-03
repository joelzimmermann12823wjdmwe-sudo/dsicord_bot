import discord
from discord import app_commands
from discord.ext import commands

class TESTWELCOME(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="testwelcome", description="Befehl: testwelcome")
    async def testwelcome(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /testwelcome wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TESTWELCOME(bot))