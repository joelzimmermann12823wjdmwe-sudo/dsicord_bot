import discord
from discord import app_commands
from discord.ext import commands
import datetime

class vcmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vcmute", description="User im Voice stumm schalten")
    @app_commands.checks.has_permissions(mute_members=True)
    async def vcmute(self, itx: discord.Interaction, user: discord.Member): await user.edit(mute=True); await itx.followup.send(f'ðŸ”‡ **{user}** wurde im Voice gemuted.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(vcmute(bot))
