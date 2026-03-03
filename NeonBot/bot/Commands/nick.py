import discord
from discord import app_commands
from discord.ext import commands

class NICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nick", description="Befehl: nick")
    async def nick(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /nick wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NICK(bot))