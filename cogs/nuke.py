import discord
from discord.ext import commands
import datetime

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nuke", description="Erneuert den Kanal")
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        pos = ctx.channel.position
        new = await ctx.channel.clone()
        await ctx.channel.delete()
        await new.edit(position=pos)
        await new.send("☢️ Kanal erfolgreich gesprengt und erneuert!")

async def setup(bot):
    await bot.add_cog(Nuke(bot))