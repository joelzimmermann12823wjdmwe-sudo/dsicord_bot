import discord
from discord import app_commands
from discord.ext import commands
import datetime

class unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unban", description="User per ID entbannen")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, itx: discord.Interaction, user_id: str, grund: str = 'Kein Grund'): user = await self.bot.fetch_user(int(user_id)); await itx.guild.unban(user, reason=grund); await itx.followup.send(f'ðŸ•Šï¸ **{user}** wurde entbannt.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(unban(bot))
