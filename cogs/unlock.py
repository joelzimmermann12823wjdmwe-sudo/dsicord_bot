import discord
from discord.ext import commands

class Unlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.hybrid_command(name="unlock", description="Entsperrt einen Kanal wieder.")
    async def unlock(self, ctx: commands.Context, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True, add_reactions=True)
        await ctx.send(f"🔓 {channel.mention} wurde entsperrt.")


async def setup(bot):
    await bot.add_cog(Unlock(bot))
