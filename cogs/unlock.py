import discord
from discord.ext import commands

class Unlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unlock", description="Entsperrt den aktuellen Kanal wieder.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Dieser Kanal wurde **entsperrt**.")

async def setup(bot):
    await bot.add_cog(Unlock(bot))
