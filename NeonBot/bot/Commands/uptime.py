import discord
from discord import app_commands
from discord.ext import commands

class UPTIME(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="uptime", description="Befehl: uptime")
    async def uptime(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /uptime wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UPTIME(bot))