import discord
from discord import app_commands
from discord.ext import commands

class UNLOCKDOWN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unlockdown", description="Befehl: unlockdown")
    async def unlockdown(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /unlockdown wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNLOCKDOWN(bot))