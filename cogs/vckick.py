import discord
from discord.ext import commands
import datetime
import asyncio

class Vckick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vckick")
    async def vckick(self, ctx, m: discord.Member): await m.move_to(None); await ctx.send(f"👢 {m} aus VC geworfen.")

async def setup(bot):
    await bot.add_cog(Vckick(bot))