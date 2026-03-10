import discord
from discord.ext import commands
import datetime

class Serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo", description="Zeigt nützliche Statistiken und Infos über diesen Server.")
    async def serverinfo(self, ctx):
        g = ctx.guild
        e = discord.Embed(title=f"Server Info: {g.name}", color=0x00ffff)
        e.add_field(name="Mitglieder", value=g.member_count)
        await ctx.send(embed=e)

async def setup(bot):
    await bot.add_cog(Serverinfo(bot))