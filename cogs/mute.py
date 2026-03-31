import discord
from discord.ext import commands

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_roles=True)
    @commands.hybrid_command(name="mute")
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        if not discord.utils.get(ctx.guild.roles, name="Muted"):
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, add_reactions=False)
        else:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"✅ {member.mention} wurde stummgeschaltet.")


async def setup(bot):
    await bot.add_cog(Mute(bot))
