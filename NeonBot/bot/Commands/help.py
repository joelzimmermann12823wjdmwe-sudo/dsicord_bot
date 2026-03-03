import discord
from discord import app_commands
from discord.ext import commands

class HELP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Befehl: help")
    async def help(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /help wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(HELP(bot))