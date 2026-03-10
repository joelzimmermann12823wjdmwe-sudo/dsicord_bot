import discord
from discord.ext import commands
import datetime

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nick", description="Ändert den Nicknamen eines Nutzers auf dem Server.")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, name: str):
        await member.edit(nick=name)
        await ctx.send(f"📝 Nickname geändert zu {name}.")

async def setup(bot):
    await bot.add_cog(Nick(bot))