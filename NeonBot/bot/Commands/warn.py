import discord
from discord import app_commands
from discord.ext import commands

class WARN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Befehl: warn")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction , user: discord.Member, grund: str):
        try:
            await interaction.response.send_message(f'⚠️ **WARNUNG** {user.mention} \n**Grund:** {grund}')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WARN(bot))