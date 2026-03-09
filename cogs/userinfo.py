import discord
from discord import app_commands
from discord.ext import commands

class UserinfoCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="userinfo", description="Zeigt Infos über einen Nutzer")
    async def userinfo(self, itx: discord.Interaction, member: discord.Member):
        await itx.response.defer(ephemeral=False)
        embed = discord.Embed(title=f"Info über {member.name}", color=member.color)
        embed.add_field(name="Beigetreten", value=member.joined_at.strftime("%d.%m.%Y"))
        embed.add_field(name="Account erstellt", value=member.created_at.strftime("%d.%m.%Y"))
        if member.avatar: embed.set_thumbnail(url=member.avatar.url)
        await itx.followup.send(embed=embed)
async def setup(bot): await bot.add_cog(UserinfoCog(bot))
