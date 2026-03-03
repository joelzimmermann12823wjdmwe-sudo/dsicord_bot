import discord
from discord import app_commands
from discord.ext import commands

class CLEARBOT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clearbot", description="Befehl: clearbot")
    async def clearbot(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /clearbot wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CLEARBOT(bot))