import discord
from discord.ext import commands
import datetime
import asyncio

class Vcunmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcunmute")
    async def vcunmute(self, ctx, m: discord.Member): await m.edit(mute=False); await ctx.send(f"🔊 {m} in VC entmutet.")

async def setup(bot):
    await bot.add_cog(Vcunmute(bot))