import discord
from discord import app_commands
from discord.ext import commands

class UNDEAFEN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="undeafen", description="Befehl: undeafen")
    async def undeafen(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /undeafen wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNDEAFEN(bot))