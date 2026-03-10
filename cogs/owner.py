import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="owner", description="Befehl owner")
    async def owner(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (owner) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Owner(bot))