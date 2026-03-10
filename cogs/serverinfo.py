import discord
from discord.ext import commands
import datetime

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo", description="Infos zum Server")
    async def serverinfo(self, ctx):
        g = ctx.guild
        embed = discord.Embed(title=f"Serverinfo: {g.name}", color=0x00ffff)
        embed.add_field(name="Mitglieder", value=g.member_count)
        embed.add_field(name="Erstellt am", value=g.created_at.strftime('%d.%m.%Y'))
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))