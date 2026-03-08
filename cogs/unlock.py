import discord
from discord import app_commands
from discord.ext import commands
import datetime

class unlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unlock", description="Kanal wieder freigeben")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, itx: discord.Interaction): await itx.channel.set_permissions(itx.guild.default_role, send_messages=True); await itx.followup.send('ðŸ”“ Kanal entsperrt.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(unlock(bot))
