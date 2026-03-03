import discord
from discord import app_commands
from discord.ext import commands

class VCMUTE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vcmute", description="Befehl: vcmute")
    @app_commands.checks.has_permissions(mute_members=True)
    async def vcmute(self, interaction: discord.Interaction , user: discord.Member):
        try:
            await user.edit(mute=True); await interaction.response.send_message(f'🔇 {user.name} im Voice stummgeschaltet.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VCMUTE(bot))