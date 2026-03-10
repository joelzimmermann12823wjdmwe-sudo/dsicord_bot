import discord
from discord.ext import commands
import datetime
import asyncio

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nick")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, name: str): await member.edit(nick=name); await ctx.send(f"📝 Name geändert zu {name}.")

async def setup(bot):
    await bot.add_cog(Nick(bot))