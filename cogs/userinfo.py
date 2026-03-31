import discord
from discord.ext import commands

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo")
    async def user_info(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Nutzerinformationen für {member}")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Erstellt am", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Beigetreten am", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unbekannt")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UserInfo(bot))
