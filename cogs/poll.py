import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="poll", description="Erstellt eine Umfrage mit Ja/Nein-Reaktionen.")
    async def poll(self, ctx: commands.Context, *, question: str):
        message = await ctx.send(f"📊 Umfrage: {question}")
        await message.add_reaction("👍")
        await message.add_reaction("👎")


async def setup(bot):
    await bot.add_cog(Poll(bot))
