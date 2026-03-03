import discord
from discord import app_commands
from discord.ext import commands

class TEMPBAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tempban", description="Befehl: tempban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def tempban(self, interaction: discord.Interaction , user: discord.Member, minuten: int, grund: str = 'Tempban'):
        try:
            import asyncio; await user.ban(reason=grund); await interaction.response.send_message(f'⏳ {user.mention} für {minuten}m gebannt.'); await asyncio.sleep(minuten*60); await interaction.guild.unban(user)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TEMPBAN(bot))