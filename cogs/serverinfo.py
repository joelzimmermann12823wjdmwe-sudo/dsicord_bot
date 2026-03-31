import discord
from discord.ext import commands
from helpers import create_embed

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo", description="Zeigt Informationen zum aktuellen Server an.")
    async def server_info(self, ctx: commands.Context):
        guild = ctx.guild
        embed = create_embed(
            title=guild.name,
            description=guild.description or "Keine Beschreibung.",
            footer="Serverinformationen",
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.add_field(name="Server-ID", value=guild.id, inline=True)
        embed.add_field(name="Mitglieder", value=guild.member_count, inline=True)
        embed.add_field(name="Erstellt am", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Region", value=str(getattr(guild, 'region', 'N/A')), inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
