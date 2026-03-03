import discord
from discord import app_commands
from discord.ext import commands

class KICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Befehl: kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction , user: discord.Member, grund: str = 'Kein Grund'):
        try:
            await user.kick(reason=grund); await interaction.response.send_message(f'👢 {user.mention} wurde gekickt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(KICK(bot))