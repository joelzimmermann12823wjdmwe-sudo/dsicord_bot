import discord
from discord import app_commands
from discord.ext import commands

class VCUNMUTE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vcunmute", description="Befehl: vcunmute")
    @app_commands.checks.has_permissions(mute_members=True)
    async def vcunmute(self, interaction: discord.Interaction , user: discord.Member):
        try:
            await user.edit(mute=False); await interaction.response.send_message(f'🔊 Stummschaltung von {user.name} aufgehoben.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VCUNMUTE(bot))