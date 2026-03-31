import discord
from discord.ext import commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="invite")
    async def invite(self, ctx: commands.Context):
        await ctx.send("🔗 Einladung: Erstelle einen Bot-Invite-Link in der Discord-Entwicklerkonsole und füge ihn deinem Server hinzu.")


async def setup(bot):
    await bot.add_cog(Invite(bot))
