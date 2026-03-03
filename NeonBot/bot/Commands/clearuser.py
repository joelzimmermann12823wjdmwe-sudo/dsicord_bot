import discord
from discord import app_commands
from discord.ext import commands

class CLEARUSER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clearuser", description="Befehl: clearuser")
    async def clearuser(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /clearuser wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CLEARUSER(bot))