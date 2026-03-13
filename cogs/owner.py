import discord
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="owner", description="Exklusive Befehle für den Bot-Entwickler.")
    @commands.is_owner()
    async def owner(self, ctx):
        await ctx.send("👑 Willkommen Meister. Alle Systeme laufen reibungslos.")

async def setup(bot):
    await bot.add_cog(Owner(bot))
