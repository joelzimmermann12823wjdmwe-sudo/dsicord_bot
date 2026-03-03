import discord
from discord import app_commands
from discord.ext import commands
import time
from datetime import datetime

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

    @app_commands.command(name="userinfo", description="User Details")
    async def userinfo(self, itn: discord.Interaction, member: discord.Member = None):
        member = member or itn.user
        embed = discord.Embed(title=f"Info: {member.name}", color=0x00f0ff)
        embed.add_field(name="Account erstellt", value=f"<t:{int(member.created_at.timestamp())}:R>")
        embed.add_field(name="Server beigetreten", value=f"<t:{int(member.joined_at.timestamp())}:R>")
        embed.set_thumbnail(url=member.display_avatar.url)
        await itn.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Zeigt Avatar")
    async def avatar(self, itn: discord.Interaction, member: discord.Member = None):
        member = member or itn.user
        await itn.response.send_message(member.display_avatar.url)

    @app_commands.command(name="ping", description="Latenz")
    async def ping(self, itn: discord.Interaction):
        await itn.response.send_message(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="uptime", description="Online seit")
    async def uptime(self, itn: discord.Interaction):
        delta = datetime.now() - self.start_time
        await itn.response.send_message(f"🕒 Online seit: {str(delta).split('.')[0]}")

async def setup(bot):
    await bot.add_cog(Utility(bot))
