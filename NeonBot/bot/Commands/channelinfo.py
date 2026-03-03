import discord
from discord import app_commands
from discord.ext import commands

class CHANNELINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="channelinfo", description="Befehl: channelinfo")
    async def channelinfo(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /channelinfo wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CHANNELINFO(bot))