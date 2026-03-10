import discord
from discord.ext import commands

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unban", description="Befehl unban")
    async def unban(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (unban) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Unban(bot))