import discord
from discord import app_commands
from discord.ext import commands

class PING(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Befehl: ping")
    async def ping(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /ping wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PING(bot))