import discord
from discord import app_commands
from discord.ext import commands

class UNLOCK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unlock", description="Befehl: unlock")
    async def unlock(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /unlock wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNLOCK(bot))