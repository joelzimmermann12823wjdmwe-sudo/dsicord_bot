import discord
from discord.ext import commands

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_roles=True)
    @commands.hybrid_command(name="unmute")
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"✅ {member.mention} wurde entmutet.")
        else:
            await ctx.send("⚠️ Der Nutzer ist nicht stummgeschaltet.")


async def setup(bot):
    await bot.add_cog(Unmute(bot))
