import discord
from discord import app_commands
from discord.ext import commands
import datetime

class vcunmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vcunmute", description="Voice-Mute aufheben")
    @app_commands.checks.has_permissions(mute_members=True)
    async def vcunmute(self, itx: discord.Interaction, user: discord.Member): await user.edit(mute=False); await itx.response.send_message(f'🔊 **{user}** ist im Voice wieder hörbar.')

async def setup(bot):
    await bot.add_cog(vcunmute(bot))