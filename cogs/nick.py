import discord
from discord import app_commands
from discord.ext import commands
import datetime

class nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nick", description="Nickname ändern")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(self, itx: discord.Interaction, user: discord.Member, name: str): await user.edit(nick=name); await itx.response.send_message(f'✅ Nickname geändert.')

async def setup(bot):
    await bot.add_cog(nick(bot))