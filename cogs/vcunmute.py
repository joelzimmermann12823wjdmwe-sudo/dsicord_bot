import discord
from discord.ext import commands

class VcUnmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vcunmute", description="Hebt die Stummschaltung im Sprachkanal auf.")
    @commands.has_permissions(mute_members=True)
    async def vcunmute(self, ctx, member: discord.Member):
        if member.voice:
            await member.edit(mute=False)
            await ctx.send(f"🎙️ **{member.display_name}** kann im Sprachkanal wieder sprechen.")
        else:
            await ctx.send("❌ Dieser Nutzer ist nicht in einem Sprachkanal.")

async def setup(bot):
    await bot.add_cog(VcUnmute(bot))
