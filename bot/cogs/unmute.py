import discord
from discord import app_commands
from discord.ext import commands
import datetime

class unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unmute", description="Timeout aufheben")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, itx: discord.Interaction, user: discord.Member): await user.timeout(None); await itx.response.send_message(f'✅ Mute aufgehoben: {user}')

async def setup(bot):
    await bot.add_cog(unmute(bot))