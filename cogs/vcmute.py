import discord
from discord.ext import commands
import datetime

class Vcmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcmute", description="Schaltet das Mikrofon eines Nutzers im Sprachkanal stumm.")
    @commands.has_permissions(mute_members=True)
    async def vcmute(self, ctx, member: discord.Member):
        await member.edit(mute=True)
        await ctx.send(f"🔇 {member.name} im Voice gemutet.")

async def setup(bot):
    await bot.add_cog(Vcmute(bot))