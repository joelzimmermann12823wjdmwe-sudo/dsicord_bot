import discord
from discord import app_commands
from discord.ext import commands

class REMOVEROLE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="removerole", description="Befehl: removerole")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removerole(self, interaction: discord.Interaction , user: discord.Member, rolle: discord.Role):
        try:
            await user.remove_roles(rolle); await interaction.response.send_message(f'❌ Rolle {rolle.name} von {user.name} entfernt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(REMOVEROLE(bot))