import discord
from discord import app_commands
from discord.ext import commands

class VCKICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vckick", description="Befehl: vckick")
    @app_commands.checks.has_permissions(move_members=True)
    async def vckick(self, interaction: discord.Interaction , user: discord.Member):
        try:
            if user.voice: await user.move_to(None); await interaction.response.send_message(f'👢 {user.name} aus Voice gekickt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VCKICK(bot))