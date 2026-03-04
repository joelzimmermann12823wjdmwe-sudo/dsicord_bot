import discord
from discord import app_commands
from discord.ext import commands
import datetime

class mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Timeout setzen")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, itx: discord.Interaction, user: discord.Member, dauer: int, grund: str = 'Kein Grund'): until = discord.utils.utcnow() + datetime.timedelta(minutes=dauer); await user.timeout(until, reason=grund); await itx.response.send_message(f'✅ Muted: {user} für {dauer} Min.')

async def setup(bot):
    await bot.add_cog(mute(bot))