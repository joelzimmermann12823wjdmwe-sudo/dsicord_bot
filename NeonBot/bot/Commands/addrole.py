import discord
from discord import app_commands
from discord.ext import commands

class ADDROLE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addrole", description="Befehl: addrole")
    async def addrole(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /addrole wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ADDROLE(bot))