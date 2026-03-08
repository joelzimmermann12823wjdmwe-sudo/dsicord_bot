import discord
from discord import app_commands
from discord.ext import commands
import datetime

class nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nick", description="Nickname Ã¤ndern")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(self, itx: discord.Interaction, user: discord.Member, name: str): await user.edit(nick=name); await itx.followup.send(f'âœï¸ Nickname geÃ¤ndert zu **{name}**.')
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(nick(bot))
