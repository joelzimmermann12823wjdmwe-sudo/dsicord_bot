import discord
from discord import app_commands
from discord.ext import commands

class SETLOGCHANNEL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setlogchannel", description="Befehl: setlogchannel")
    async def setlogchannel(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /setlogchannel wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SETLOGCHANNEL(bot))