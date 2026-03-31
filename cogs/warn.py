import discord
from discord.ext import commands
from helpers import create_embed

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="warn", description="Verwarnt einen Nutzer und speichert die Verwarnung.")
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "keine Angabe"):
        warn_count = self.bot.storage.add_warn(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            reason,
        )
        embed = create_embed(
            title="⚠️ Nutzer verwarnt",
            description=f"{member.mention} wurde verwarnt.",
            footer=f"Warns gesamt: {warn_count}",
        )
        embed.add_field(name="Grund", value=reason, inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Warn(bot))
