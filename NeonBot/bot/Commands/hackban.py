import discord
from discord import app_commands
from discord.ext import commands

class HACKBAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hackban", description="Befehl: hackban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def hackban(self, interaction: discord.Interaction , user_id: str, grund: str = 'ID-Ban'):
        try:
            await interaction.guild.ban(discord.Object(id=int(user_id)), reason=grund); await interaction.response.send_message(f'💻 ID {user_id} wurde vorab gebannt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(HACKBAN(bot))