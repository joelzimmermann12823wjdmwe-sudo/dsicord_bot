import discord
from discord import app_commands
from discord.ext import commands

class SOFTBAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="softban", description="Befehl: softban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def softban(self, interaction: discord.Interaction , user: discord.Member, grund: str = 'Softban'):
        try:
            await user.ban(reason=grund, delete_message_days=7); await interaction.guild.unban(user); await interaction.response.send_message(f'💨 Softban: {user.name} gekickt & Nachrichten gelöscht.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SOFTBAN(bot))