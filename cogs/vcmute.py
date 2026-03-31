import discord
from discord.ext import commands

class VcMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcmute", description="Schaltet einen Nutzer im Sprachkanal stumm.")
    @commands.has_permissions(mute_members=True)
    async def vcmute(self, ctx, member: discord.Member):
        if member.voice:
            await member.edit(mute=True)
            await ctx.send(f"🎙️ **{member.display_name}** wurde im Sprachkanal stummgeschaltet.")
        else:
            await ctx.send("❌ Dieser Nutzer ist nicht in einem Sprachkanal.")

async def setup(bot):
    await bot.add_cog(VcMute(bot))
