import discord
from discord.ext import commands
import datetime
import asyncio

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nuke")
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx): new = await ctx.channel.clone(); await ctx.channel.delete(); await new.send("☢️ Kanal erneuert.")

async def setup(bot):
    await bot.add_cog(Nuke(bot))