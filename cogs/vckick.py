import discord
from discord import app_commands
from discord.ext import commands

class VckickCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="vckick", description="Kickt einen Nutzer aus dem Voice-Kanal")
    @app_commands.default_permissions(move_members=True)
    async def vckick(self, itx: discord.Interaction, member: discord.Member):
        await itx.response.defer(ephemeral=True)
        if member.voice:
            await member.move_to(None)
            await itx.followup.send(f"✅ {member.mention} wurde aus dem Voice gekickt.")
        else:
            await itx.followup.send("❌ Nutzer ist in keinem Voice-Kanal.")
async def setup(bot): await bot.add_cog(VckickCog(bot))
