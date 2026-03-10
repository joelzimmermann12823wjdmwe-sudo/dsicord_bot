import discord
from discord.ext import commands
import datetime

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Prüft die Latenz")
    async def ping(self, ctx):
        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

async def setup(bot):
    await bot.add_cog(Ping(bot))