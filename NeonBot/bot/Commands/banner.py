import discord
from discord import app_commands
from discord.ext import commands

class BANNER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="banner", description="Befehl: banner")
    async def banner(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /banner wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BANNER(bot))