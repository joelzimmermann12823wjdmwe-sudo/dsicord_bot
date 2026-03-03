import discord
from discord import app_commands
from discord.ext import commands

class AVATAR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Befehl: avatar")
    async def avatar(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /avatar wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AVATAR(bot))