import discord
from discord import app_commands
from discord.ext import commands
import datetime

class nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nuke", description="Kanal klonen und lÃ¶schen (kompletter Reset)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def nuke(self, itx: discord.Interaction): pos = itx.channel.position; new_ch = await itx.channel.clone(); await new_ch.edit(position=pos); await itx.channel.delete(); await new_ch.send('â˜¢ï¸ **Kanal wurde genuked!**')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(nuke(bot))
