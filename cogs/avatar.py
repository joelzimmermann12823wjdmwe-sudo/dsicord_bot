import discord
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar", description="Zeigt das Profilbild eines Nutzers.")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Avatar von {member.name}", color=discord.Color.purple())
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Avatar(bot))
