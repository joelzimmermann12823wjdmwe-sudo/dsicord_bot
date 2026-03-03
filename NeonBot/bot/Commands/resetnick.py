import discord
from discord import app_commands
from discord.ext import commands

class RESETNICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="resetnick", description="Befehl: resetnick")
    async def resetnick(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /resetnick wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RESETNICK(bot))