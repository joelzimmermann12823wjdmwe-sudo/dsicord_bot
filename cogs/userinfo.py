import discord
from discord.ext import commands

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo", description="Zeigt Informationen über einen bestimmten Benutzer an.")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        embed = discord.Embed(title=f"Benutzerinfo - {member.display_name}", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        embed.add_field(name="Benutzername", value=member.name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Account erstellt", value=discord.utils.format_dt(member.created_at, "F"), inline=False)
        embed.add_field(name="Server beigetreten", value=discord.utils.format_dt(member.joined_at, "F"), inline=False)
        embed.add_field(name="Höchste Rolle", value=member.top_role.mention, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))
