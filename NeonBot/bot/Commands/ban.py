import discord
from discord import app_commands
from discord.ext import commands

class BAN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Befehl: ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction , user: discord.Member, grund: str = 'Kein Grund'):
        try:
            await user.ban(reason=grund); await interaction.response.send_message(f'🔨 {user.mention} wurde permanent verbannt.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BAN(bot))