import discord
from discord import app_commands
from discord.ext import commands

class BOTINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="botinfo", description="Befehl: botinfo")
    async def botinfo(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /botinfo wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BOTINFO(bot))