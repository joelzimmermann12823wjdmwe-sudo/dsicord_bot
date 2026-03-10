import discord
from discord.ext import commands

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nick", description="Befehl nick")
    async def nick(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (nick) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Nick(bot))