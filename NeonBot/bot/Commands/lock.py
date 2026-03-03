import discord
from discord import app_commands
from discord.ext import commands

class LOCK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lock", description="Befehl: lock")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction ):
        try:
            await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False); await interaction.response.send_message('🔒 Kanal für @everyone gesperrt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LOCK(bot))