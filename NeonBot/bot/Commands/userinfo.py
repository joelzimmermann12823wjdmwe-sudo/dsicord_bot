import discord
from discord import app_commands
from discord.ext import commands

class USERINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Befehl: userinfo")
    async def userinfo(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /userinfo wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(USERINFO(bot))