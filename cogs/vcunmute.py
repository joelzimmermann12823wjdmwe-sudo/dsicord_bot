import discord
from discord.ext import commands
import datetime

class Vcunmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcunmute", description="Entmutet das Mikrofon eines Nutzers im Sprachkanal.")
    @commands.has_permissions(mute_members=True)
    async def vcunmute(self, ctx, member: discord.Member):
        await member.edit(mute=False)
        await ctx.send(f"🔊 {member.name} im Voice entmutet.")

async def setup(bot):
    await bot.add_cog(Vcunmute(bot))