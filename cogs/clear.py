import discord
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear", description="Befehl clear")
    async def clear(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (clear) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Clear(bot))