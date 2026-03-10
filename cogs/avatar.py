import discord
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar", description="Befehl avatar")
    async def avatar(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (avatar) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Avatar(bot))