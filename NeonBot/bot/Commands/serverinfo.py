import discord
from discord import app_commands
from discord.ext import commands

class SERVERINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Befehl: serverinfo")
    async def serverinfo(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /serverinfo wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SERVERINFO(bot))