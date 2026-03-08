import discord
from discord import app_commands
from discord.ext import commands
import datetime

class slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="Slowmode setzen (Sekunden)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, itx: discord.Interaction, sekunden: int): await itx.channel.edit(slowmode_delay=sekunden); await itx.followup.send(f'â±ï¸ Slowmode auf {sekunden} Sekunden gesetzt.')
        await itx.response.defer(ephemeral=True)


async def setup(bot):
    await bot.add_cog(slowmode(bot))
