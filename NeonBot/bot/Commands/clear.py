import discord
from discord import app_commands
from discord.ext import commands

class CLEAR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Befehl: clear")
    async def clear(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /clear wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CLEAR(bot))