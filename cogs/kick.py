import discord
from discord import app_commands
from discord.ext import commands
import datetime

class kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="User vom Server kicken")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, itx: discord.Interaction, user: discord.Member, grund: str = 'Kein Grund'): await user.kick(reason=grund); await itx.followup.send(f'ðŸ‘¢ **{user}** wurde gekickt. Grund: {grund}')
        await itx.response.defer(ephemeral=True)


async def setup(bot):
    await bot.add_cog(kick(bot))
