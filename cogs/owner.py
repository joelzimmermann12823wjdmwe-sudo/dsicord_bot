import discord
from discord.ext import commands
import datetime

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("💤 Fahre herunter...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Owner(bot))