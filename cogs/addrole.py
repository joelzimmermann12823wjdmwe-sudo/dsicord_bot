import discord
from discord import app_commands
from discord.ext import commands
import datetime

class addrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addrole", description="Rolle an User vergeben")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole(self, itx: discord.Interaction, user: discord.Member, rolle: discord.Role): await user.add_roles(rolle); await itx.followup.send(f'âœ… **{user.name}** hat nun die Rolle **{rolle.name}**.')
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(addrole(bot))
