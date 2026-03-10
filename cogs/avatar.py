import discord
from discord.ext import commands
import datetime

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar", description="Zeigt das Profilbild (Avatar) eines Nutzers in groß.")
    async def avatar(self, ctx, member: discord.Member=None):
        member = member or ctx.author
        await ctx.send(member.display_avatar.url)

async def setup(bot):
    await bot.add_cog(Avatar(bot))