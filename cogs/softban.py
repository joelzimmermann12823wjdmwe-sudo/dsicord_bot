import discord
from discord import app_commands
from discord.ext import commands
import datetime

class softban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="softban", description="Bannen und sofort entbannen (lÃ¶scht Nachrichten)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def softban(self, itx: discord.Interaction, user: discord.Member, grund: str = 'Kein Grund'): await itx.guild.ban(user, reason=grund, delete_message_days=7); await itx.guild.unban(user, reason='Softban'); await itx.followup.send(f'ðŸ§¹ **{user}** wurde ge-softbant.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(softban(bot))
