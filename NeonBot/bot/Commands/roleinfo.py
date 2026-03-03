import discord
from discord import app_commands
from discord.ext import commands

class ROLEINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roleinfo", description="Befehl: roleinfo")
    async def roleinfo(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /roleinfo wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ROLEINFO(bot))