import discord
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.hybrid_command(name="lock", description="Sperrt einen Kanal für normale Mitglieder.")
    async def lock(self, ctx: commands.Context, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False, add_reactions=False)
        await ctx.send(f"🔒 {channel.mention} wurde gesperrt.")


async def setup(bot):
    await bot.add_cog(Lock(bot))
