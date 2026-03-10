import discord
from discord.ext import commands
import datetime

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear", description="Löscht eine bestimmte Anzahl an Nachrichten im Kanal.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, anzahl: int):
        await ctx.channel.purge(limit=anzahl)
        await ctx.send(f"🧹 {anzahl} Nachrichten gelöscht.", delete_after=3)

async def setup(bot):
    await bot.add_cog(Clear(bot))