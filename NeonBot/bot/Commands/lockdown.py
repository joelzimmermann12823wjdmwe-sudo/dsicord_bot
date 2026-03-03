import discord
from discord import app_commands
from discord.ext import commands

class LOCKDOWN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lockdown", description="Befehl: lockdown")
    async def lockdown(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /lockdown wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LOCKDOWN(bot))