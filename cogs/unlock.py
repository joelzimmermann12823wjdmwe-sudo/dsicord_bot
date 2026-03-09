import discord
from discord import app_commands
from discord.ext import commands

class UnlockCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="unlock", description="Entsperrt den aktuellen Kanal")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=False)
        await itx.channel.set_permissions(itx.guild.default_role, send_messages=True)
        await itx.followup.send("🔓 Dieser Kanal wurde wieder entsperrt.")
async def setup(bot): await bot.add_cog(UnlockCog(bot))
