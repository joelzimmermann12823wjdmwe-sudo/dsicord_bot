import discord
from discord import app_commands
from discord.ext import commands
import datetime

class vckick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="vckick", description="User aus dem Voice werfen")
    @app_commands.checks.has_permissions(move_members=True)
    async def vckick(self, itx: discord.Interaction, user: discord.Member): await user.move_to(None); await itx.followup.send(f'ðŸšª **{user}** wurde aus dem Voice gekickt.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(vckick(bot))
