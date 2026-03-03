import discord
from discord import app_commands
from discord.ext import commands
from .helper import load_data, save_data

class SetupInfo(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setlog", description="Log-Channel setzen")
    async def setlog(self, itx, channel: discord.TextChannel):
        d = load_data("config.json"); d[str(itx.guild.id)] = d.get(str(itx.guild.id), {}); d[str(itx.guild.id)]["log"] = channel.id
        save_data("config.json", d); await itx.response.send_message(f"Log: {channel.mention}")

    @app_commands.command(name="help", description="Hilfe anzeigen")
    async def help(self, itx):
        emb = discord.Embed(title="Neon Bot Hilfe", color=0x00f0ff, description="Nutze / für alle Commands.")
        await itx.response.send_message(embed=emb)

    @app_commands.command(name="botinfo", description="Bot Status")
    async def botinfo(self, itx):
        await itx.response.send_message(f"Neon Bot v2 | Latency: {round(self.bot.latency*1000)}ms")

    @app_commands.command(name="userinfo", description="User Infos")
    async def userinfo(self, itx, member: discord.Member):
        emb = discord.Embed(title=f"Info: {member}", color=0x00f0ff)
        emb.add_field(name="ID", value=member.id); await itx.response.send_message(embed=emb)

    @app_commands.command(name="serverinfo", description="Server Infos")
    async def serverinfo(self, itx):
        await itx.response.send_message(f"Server: {itx.guild.name} | Members: {itx.guild.member_count}")

    @app_commands.command(name="avatar", description="Avatar zeigen")
    async def avatar(self, itx, member: discord.Member):
        await itx.response.send_message(member.display_avatar.url)

async def setup(bot): await bot.add_cog(SetupInfo(bot))
