import discord
from discord import app_commands
from discord.ext import commands
from bot.database import get_settings

class SettingsCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="settings", description="Server-Konfiguration anzeigen")
    @app_commands.default_permissions(administrator=True)
    async def settings(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=True)
        data = get_settings(itx.guild.id)
        embed = discord.Embed(title="Server Einstellungen", color=discord.Color.blue())
        embed.add_field(name="Logging", value=f"<#{data['log_channel_id']}>" if data['log_channel_id'] else "Aus")
        embed.add_field(name="AutoMod", value="An" if data['automod_active'] else "Aus")
        await itx.followup.send(embed=embed)

async def setup(bot): await bot.add_cog(SettingsCog(bot))
