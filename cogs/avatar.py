import discord
from discord.ext import commands
from helpers import create_embed

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar", description="Zeigt den Avatar eines Nutzers an.")
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = create_embed(
            title=f"Avatar von {member}",
            description="Hier ist das Profilbild.",
            footer=f"Angefragt von {ctx.author}",
        )
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Avatar(bot))
