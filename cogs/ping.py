import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Zeigt die aktuelle Latenz (Verzögerung) des Bots an.")
    async def ping(self, ctx):
        latenz = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Die aktuelle Latenz beträgt **{latenz}ms**.")

async def setup(bot):
    await bot.add_cog(Ping(bot))
