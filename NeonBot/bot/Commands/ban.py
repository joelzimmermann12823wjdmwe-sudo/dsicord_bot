import discord
from discord import app_commands
from discord.ext import commands

class BAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Befehl: ban")
    async def ban(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /ban wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BAN(bot))