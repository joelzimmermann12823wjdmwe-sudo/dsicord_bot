import discord
from discord import app_commands
from discord.ext import commands

class VcmuteCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="vcmute", description="Schaltet einen Nutzer im Voice stumm")
    @app_commands.default_permissions(mute_members=True)
    async def vcmute(self, itx: discord.Interaction, member: discord.Member):
        await itx.response.defer(ephemeral=True)
        if member.voice:
            await member.edit(mute=True)
            await itx.followup.send(f"🔇 {member.mention} wurde im Voice stummgeschaltet.")
        else:
            await itx.followup.send("❌ Nutzer ist in keinem Voice-Kanal.")
async def setup(bot): await bot.add_cog(VcmuteCog(bot))
