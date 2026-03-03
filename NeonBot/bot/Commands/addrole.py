import discord
from discord import app_commands
from discord.ext import commands

class ADDROLE(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addrole", description="Befehl: addrole")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole(self, interaction: discord.Interaction , user: discord.Member, rolle: discord.Role):
        try:
            await user.add_roles(rolle); await interaction.response.send_message(f'✅ {user.name} hat nun die Rolle {rolle.name}.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ADDROLE(bot))