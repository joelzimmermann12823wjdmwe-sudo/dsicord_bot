import discord
from discord.ext import commands
import datetime
import asyncio

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help")
    async def help(self, ctx): e=discord.Embed(title="Neon Hilfe", color=0x00ffff); e.add_field(name="Links", value="[Website](https://neon-bot-2026.vercel.app/)\n📧 dev-jojo@proton.me"); await ctx.send(embed=e)

async def setup(bot):
    await bot.add_cog(Help(bot))