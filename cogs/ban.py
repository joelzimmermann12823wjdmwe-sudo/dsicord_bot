import discord
from discord import app_commands
from discord.ext import commands
import datetime

class ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="User permanent bannen")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, itx: discord.Interaction, user: discord.User, grund: str = 'Kein Grund'): await itx.guild.ban(user, reason=grund); await itx.response.send_message(f'🔨 **{user}** wurde gebannt. Grund: {grund}')

async def setup(bot):
    await bot.add_cog(ban(bot))