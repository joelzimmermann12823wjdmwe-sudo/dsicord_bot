import discord
from discord import app_commands
from discord.ext import commands

class WARN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Befehl: warn")
    async def warn(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /warn wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WARN(bot))