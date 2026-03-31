import discord
from discord.ext import commands

class VcKick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vckick", description="Wirft einen Nutzer aus dem Sprachkanal.")
    @commands.has_permissions(move_members=True)
    async def vckick(self, ctx, member: discord.Member):
        if member.voice:
            await member.move_to(None)
            await ctx.send(f"✅ **{member.display_name}** wurde aus dem Sprachkanal geworfen.")
        else:
            await ctx.send("❌ Dieser Nutzer befindet sich nicht in einem Sprachkanal.")

async def setup(bot):
    await bot.add_cog(VcKick(bot))
