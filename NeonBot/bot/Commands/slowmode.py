import discord
from discord import app_commands
from discord.ext import commands

class SLOWMODE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="Befehl: slowmode")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction , sekunden: int):
        try:
            await interaction.channel.edit(slowmode_delay=sekunden); await interaction.response.send_message(f'⏳ Slowmode auf {sekunden}s gesetzt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SLOWMODE(bot))