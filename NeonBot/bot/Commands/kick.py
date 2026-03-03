import discord
from discord import app_commands
from discord.ext import commands

class KICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Befehl: kick")
    async def kick(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /kick wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(KICK(bot))