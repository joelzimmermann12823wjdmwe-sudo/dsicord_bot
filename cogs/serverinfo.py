import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo")
    async def server_info(self, ctx: commands.Context):
        guild = ctx.guild
        embed = discord.Embed(title=guild.name, description=guild.description or "Keine Beschreibung.")
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.add_field(name="Server-ID", value=guild.id)
        embed.add_field(name="Region", value=str(getattr(guild, 'region', 'N/A')))
        embed.add_field(name="Mitglieder", value=guild.member_count)
        embed.add_field(name="Erstellt am", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
