import discord
from discord import app_commands
from discord.ext import commands
import datetime

class removerole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="removerole", description="Rolle von User entfernen")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removerole(self, itx: discord.Interaction, user: discord.Member, rolle: discord.Role): await user.remove_roles(rolle); await itx.response.send_message(f'❌ **{user.name}** hat die Rolle **{rolle.name}** verloren.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(removerole(bot))
