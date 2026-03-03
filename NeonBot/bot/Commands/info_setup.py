import discord
from discord import app_commands
from discord.ext import commands

class InfoSetup(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ping", description="Latenz pruefen")
    async def ping(self, itx): await itx.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="userinfo", description="Infos ueber einen Nutzer")
    async def userinfo(self, itx, member: discord.Member = None):
        member = member or itx.user
        emb = discord.Embed(title=f"Userinfo: {member}", color=0x00f0ff)
        emb.add_field(name="ID", value=member.id)
        emb.add_field(name="Joined", value=member.joined_at.strftime("%d.%m.%Y"))
        emb.set_thumbnail(url=member.display_avatar.url)
        await itx.response.send_message(embed=emb)

    @app_commands.command(name="serverinfo", description="Infos ueber den Server")
    async def serverinfo(self, itx):
        emb = discord.Embed(title=f"Server: {itx.guild.name}", color=0x00f0ff)
        emb.add_field(name="Mitglieder", value=itx.guild.member_count)
        emb.add_field(name="ID", value=itx.guild.id)
        await itx.response.send_message(embed=emb)

    @app_commands.command(name="avatar", description="Avatar eines Nutzers anzeigen")
    async def avatar(self, itx, member: discord.Member = None):
        member = member or itx.user
        await itx.response.send_message(member.display_avatar.url)

async def setup(bot): await bot.add_cog(InfoSetup(bot))
