import discord
from discord import app_commands
from discord.ext import commands

class UNDEAFEN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="undeafen", description="Befehl: undeafen")
    @app_commands.checks.has_permissions(mute_members=True)
    async def undeafen(self, interaction: discord.Interaction , user: discord.Member):
        try:
            await user.edit(deafen=False); await interaction.response.send_message(f'🔊 {user.name} kann wieder hören.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNDEAFEN(bot))