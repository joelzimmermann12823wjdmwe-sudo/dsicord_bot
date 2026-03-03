import discord
from discord import app_commands
from discord.ext import commands

class DELWARN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="delwarn", description="Befehl: delwarn")
    async def delwarn(self, interaction: discord.Interaction):
        # Basis-Antwort für den Command
        await interaction.response.send_message(f"Befehl /delwarn wurde erfolgreich geladen!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DELWARN(bot))