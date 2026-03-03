import discord
from discord import app_commands
from discord.ext import commands

class SOFTBAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="softban", description="Befehl: softban")
    async def softban(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /softban wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SOFTBAN(bot))