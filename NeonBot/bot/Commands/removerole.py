import discord
from discord import app_commands
from discord.ext import commands

class REMOVEROLE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="removerole", description="Befehl: removerole")
    async def removerole(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /removerole wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(REMOVEROLE(bot))