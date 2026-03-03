import discord
from discord import app_commands
from discord.ext import commands

class TICKETSETUP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketsetup", description="Befehl: ticketsetup")
    async def ticketsetup(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /ticketsetup wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TICKETSETUP(bot))