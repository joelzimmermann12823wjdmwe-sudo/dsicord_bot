import discord
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="lock", description="Sperrt den aktuellen Kanal für normale Nutzer.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Dieser Kanal wurde **gesperrt**.")

async def setup(bot):
    await bot.add_cog(Lock(bot))
