import discord
from discord import app_commands
from discord.ext import commands

class AvatarCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="avatar", description="Zeigt das Profilbild an")
    async def avatar(self, itx: discord.Interaction, member: discord.Member):
        await itx.response.defer(ephemeral=False)
        embed = discord.Embed(title=f"Avatar von {member.name}", color=discord.Color.blue())
        if member.avatar:
            embed.set_image(url=member.avatar.url)
            await itx.followup.send(embed=embed)
        else:
            await itx.followup.send("Dieser Nutzer hat kein Profilbild.")
async def setup(bot): await bot.add_cog(AvatarCog(bot))
