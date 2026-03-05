import discord
from discord import app_commands
from discord.ext import commands
import datetime

class avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Avatar in Groß anzeigen")
    @app_commands.checks.has_permissions(send_messages=True)
    async def avatar(self, itx: discord.Interaction, user: discord.User): embed = discord.Embed(title=f'Avatar von {user.name}', color=discord.Color.teal()); embed.set_image(url=user.display_avatar.url); await itx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(avatar(bot))