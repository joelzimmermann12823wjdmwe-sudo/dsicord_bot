import discord
from discord import app_commands
from discord.ext import commands

class LockCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="lock", description="Sperrt den aktuellen Kanal")
    @app_commands.default_permissions(manage_channels=True)
    async def lock(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=False) # Jeder soll das sehen
        await itx.channel.set_permissions(itx.guild.default_role, send_messages=False)
        await itx.followup.send("🔒 Dieser Kanal wurde gesperrt.")
async def setup(bot): await bot.add_cog(LockCog(bot))
