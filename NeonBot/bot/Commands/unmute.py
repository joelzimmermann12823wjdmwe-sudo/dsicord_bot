import discord
from discord import app_commands
from discord.ext import commands

class UNMUTE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unmute", description="Befehl: unmute")
    async def unmute(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /unmute wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNMUTE(bot))