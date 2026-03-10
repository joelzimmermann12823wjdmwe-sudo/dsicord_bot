import discord
from discord.ext import commands

class Userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="userinfo", description="Befehl userinfo")
    async def userinfo(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (userinfo) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Userinfo(bot))