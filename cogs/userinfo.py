import discord
from discord.ext import commands
import datetime

class Userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo", description="Zeigt detaillierte Informationen über einen Nutzer an.")
    async def userinfo(self, ctx, member: discord.Member=None):
        member = member or ctx.author
        e = discord.Embed(title=f"User Info: {member.name}", color=member.color)
        e.add_field(name="ID", value=member.id)
        e.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=e)

async def setup(bot):
    await bot.add_cog(Userinfo(bot))