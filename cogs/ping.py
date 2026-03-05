import discord
from discord import app_commands
from discord.ext import commands
import datetime

class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Bot-Latenz anzeigen")
    @app_commands.checks.has_permissions(send_messages=True)
    async def ping(self, itx: discord.Interaction): await itx.response.send_message(f'🏓 Pong! **{round(self.bot.latency * 1000)}ms**')

async def setup(bot):
    await bot.add_cog(ping(bot))