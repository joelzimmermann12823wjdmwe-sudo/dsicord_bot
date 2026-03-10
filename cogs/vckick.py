import discord
from discord.ext import commands
import datetime

class Vckick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vckick", description="Wirft einen Nutzer aus seinem aktuellen Sprachkanal.")
    @commands.has_permissions(move_members=True)
    async def vckick(self, ctx, member: discord.Member):
        if member.voice:
            await member.move_to(None)
            await ctx.send(f"👢 {member.name} aus dem Voice gekickt.")
        else:
            await ctx.send("Dieser Nutzer ist nicht im Voice-Channel.")

async def setup(bot):
    await bot.add_cog(Vckick(bot))