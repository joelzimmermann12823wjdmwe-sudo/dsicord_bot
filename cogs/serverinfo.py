import discord
from discord import app_commands
from discord.ext import commands

class ServerinfoCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="serverinfo", description="Zeigt Infos über den Server")
    async def serverinfo(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=False)
        g = itx.guild
        embed = discord.Embed(title=f"Server: {g.name}", color=discord.Color.blue())
        embed.add_field(name="Mitglieder", value=g.member_count)
        embed.add_field(name="Erstellt am", value=g.created_at.strftime("%d.%m.%Y"))
        embed.add_field(name="Besitzer", value=g.owner.mention if g.owner else "Unbekannt")
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        await itx.followup.send(embed=embed)
async def setup(bot): await bot.add_cog(ServerinfoCog(bot))
