import discord
from discord import app_commands
from discord.ext import commands

class UNBAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unban", description="Befehl: unban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction , user_id: str):
        try:
            await interaction.guild.unban(discord.Object(id=int(user_id))); await interaction.response.send_message(f'✅ User mit ID {user_id} entbannt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UNBAN(bot))