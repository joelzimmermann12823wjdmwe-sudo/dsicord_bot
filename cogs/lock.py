import discord
from discord import app_commands
from discord.ext import commands
import datetime

class lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lock", description="Kanal fÃ¼r normale User sperren")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, itx: discord.Interaction): await itx.channel.set_permissions(itx.guild.default_role, send_messages=False); await itx.followup.send('ðŸ”’ Kanal gesperrt.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(lock(bot))
