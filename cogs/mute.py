import discord
from discord import app_commands
from discord.ext import commands
import datetime

class mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Discord Timeout setzen (Minuten)")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, itx: discord.Interaction, user: discord.Member, dauer: int, grund: str = 'Kein Grund'): until = discord.utils.utcnow() + datetime.timedelta(minutes=dauer); await user.timeout(until, reason=grund); await itx.followup.send(f'ðŸ”‡ **{user}** wurde fÃ¼r {dauer} Minuten gemuted.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(mute(bot))
