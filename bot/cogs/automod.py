import discord
from discord.ext import commands

class automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        # Logik für Schimpfwörter, Links, Caps hier einfügen
        pass

async def setup(bot):
    await bot.add_cog(automod(bot))