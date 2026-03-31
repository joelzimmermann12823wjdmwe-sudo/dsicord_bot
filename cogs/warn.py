import discord
from discord.ext import commands

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="warn", description="Verwarnt einen Nutzer und speichert den Eintrag.")
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "keine Angabe"):
        warn_count = self.bot.storage.add_warn(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            reason,
        )
        await ctx.send(
            f"⚠️ {member.mention} wurde verwarnt. Grund: {reason} (Warns gesamt: {warn_count})"
        )


async def setup(bot):
    await bot.add_cog(Warn(bot))
