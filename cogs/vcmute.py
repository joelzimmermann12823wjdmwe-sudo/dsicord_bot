import discord
from discord.ext import commands
import datetime
import asyncio

class Vcmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcmute")
    async def vcmute(self, ctx, m: discord.Member): await m.edit(mute=True); await ctx.send(f"🔇 {m} in VC stumm.")

async def setup(bot):
    await bot.add_cog(Vcmute(bot))