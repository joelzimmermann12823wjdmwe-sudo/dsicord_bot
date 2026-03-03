import discord
from discord import app_commands
from discord.ext import commands

class VCMUTE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vcmute", description="Befehl: vcmute")
    async def vcmute(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /vcmute wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VCMUTE(bot))