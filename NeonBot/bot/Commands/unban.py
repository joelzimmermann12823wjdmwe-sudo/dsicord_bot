import discord
from discord import app_commands
from discord.ext import commands

class UNBAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unban", description="Befehl: unban")
    async def unban(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /unban wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNBAN(bot))