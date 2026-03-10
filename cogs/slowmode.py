import discord
from discord.ext import commands
import datetime
import asyncio

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, sek: int): await ctx.channel.edit(slowmode_delay=sek); await ctx.send(f"⏳ Slowmode: {sek}s.")

async def setup(bot):
    await bot.add_cog(Slowmode(bot))