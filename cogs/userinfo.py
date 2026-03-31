import discord
from discord.ext import commands
from helpers import create_embed

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo", description="Zeigt Informationen zu einem Nutzer an.")
    async def user_info(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = create_embed(
            title=f"Nutzerinformationen für {member}",
            description="Detaillierte Informationen zum gewählten Nutzer.",
            footer=f"Angefragt von {ctx.author}",
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Erstellt am", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Beigetreten am", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unbekannt", inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UserInfo(bot))
