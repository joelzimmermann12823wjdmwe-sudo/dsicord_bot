import discord
from discord import app_commands
from discord.ext import commands

class WARNS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warns", description="Befehl: warns")
    async def warns(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /warns wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WARNS(bot))