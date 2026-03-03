import discord
from discord import app_commands
from discord.ext import commands

class UNMUTE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unmute", description="Befehl: unmute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction , user: discord.Member):
        try:
            await user.timeout(None); await interaction.response.send_message(f'🔊 Stummschaltung für {user.mention} aufgehoben.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNMUTE(bot))