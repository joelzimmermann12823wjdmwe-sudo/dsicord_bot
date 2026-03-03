import discord
from discord import app_commands
from discord.ext import commands

class CLEARWARNS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clearwarns", description="Befehl: clearwarns")
    async def clearwarns(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /clearwarns wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CLEARWARNS(bot))