import discord
from discord.ext import commands
import time

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"Infos für {guild.name}", color=discord.Color.blue())
        embed.add_field(name="Mitglieder", value=guild.member_count)
        embed.add_field(name="Erstellt am", value=guild.created_at.strftime("%d.%m.%Y"))
        await ctx.send(embed=embed)

    # ... hier folgen intern: userinfo, avatar, banner, roles, channelinfo, 
    # uptime, invite, vote, support, stats, worldclock, translate, weather
