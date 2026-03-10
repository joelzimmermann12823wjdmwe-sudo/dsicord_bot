import discord
from discord.ext import commands

class Addrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addrole", description="Befehl addrole")
    async def addrole(self, ctx):
        await ctx.send("🛠️ Dieser Befehl (addrole) ist bereit, aber noch ohne Logik.")

async def setup(bot):
    await bot.add_cog(Addrole(bot))