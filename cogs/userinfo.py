import discord
from discord import app_commands
from discord.ext import commands
import datetime

class userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Infos Ã¼ber einen User")
    @app_commands.checks.has_permissions(send_messages=True)
    async def userinfo(self, itx: discord.Interaction, user: discord.Member): embed = discord.Embed(title=str(user), color=user.color); embed.add_field(name='ID', value=user.id); embed.add_field(name='Beigetreten', value=user.joined_at.strftime('%Y-%m-%d')); await itx.followup.send(embed=embed)
        await itx.response.defer(ephemeral=True)

async def setup(bot):
    await bot.add_cog(userinfo(bot))
