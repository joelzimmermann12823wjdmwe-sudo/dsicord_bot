import discord
from discord import app_commands
from discord.ext import commands

class MUTE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Befehl: mute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction , user: discord.Member, minuten: int, grund: str = 'Timeout'):
        try:
            import datetime; await user.timeout(datetime.timedelta(minutes=minuten), reason=grund); await interaction.response.send_message(f'🔇 {user.mention} wurde für {minuten}m stummgeschaltet.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MUTE(bot))