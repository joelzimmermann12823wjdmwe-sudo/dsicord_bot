import discord
from discord.ext import commands

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.hybrid_command(name="slowmode", description="Setzt den Slowmode für diesen Kanal.")
    async def slowmode(self, ctx: commands.Context, seconds: int = 0):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"🐢 Slowmode wurde auf {seconds} Sekunden gesetzt.")


async def setup(bot):
    await bot.add_cog(Slowmode(bot))
