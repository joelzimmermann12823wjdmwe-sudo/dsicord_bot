import discord
from discord import app_commands
from discord.ext import commands

class RESETNICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="resetnick", description="Befehl: resetnick")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def resetnick(self, interaction: discord.Interaction , user: discord.Member):
        try:
            await user.edit(nick=None); await interaction.response.send_message(f'✅ Nickname von {user.name} zurückgesetzt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RESETNICK(bot))