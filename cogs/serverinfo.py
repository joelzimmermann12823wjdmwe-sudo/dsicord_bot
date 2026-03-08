import discord
from discord import app_commands
from discord.ext import commands
import datetime

class serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Statistiken Ã¼ber den Server")
    @app_commands.checks.has_permissions(send_messages=True)
    async def serverinfo(self, itx: discord.Interaction): embed = discord.Embed(title=itx.guild.name, color=discord.Color.blue()); embed.add_field(name='Mitglieder', value=itx.guild.member_count); embed.add_field(name='Owner', value=itx.guild.owner.mention); await itx.followup.send(embed=embed)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(serverinfo(bot))
