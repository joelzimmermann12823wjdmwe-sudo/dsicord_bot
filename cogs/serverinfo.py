import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverinfo", description="Zeigt Informationen über diesen Server an.")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        
        embed = discord.Embed(title=f"Serverinfo - {guild.name}", color=discord.Color.green())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Besitzer", value=guild.owner.mention, inline=True)
        embed.add_field(name="Mitglieder", value=guild.member_count, inline=True)
        embed.add_field(name="Rollenanzahl", value=len(guild.roles), inline=True)
        embed.add_field(name="Erstellt am", value=discord.utils.format_dt(guild.created_at, "F"), inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
