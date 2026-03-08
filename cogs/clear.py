import discord
from discord import app_commands
from discord.ext import commands
import datetime

class clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Nachrichten löschen (max 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, itx: discord.Interaction, anzahl: int): deleted = await itx.channel.purge(limit=min(anzahl, 100)); await itx.response.send_message(f'🗑️ **{len(deleted)}** Nachrichten gelöscht.', ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(clear(bot))
