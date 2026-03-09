import discord
from discord import app_commands
from discord.ext import commands

class VcunmuteCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="vcunmute", description="Hebt die Voice-Stummschaltung auf")
    @app_commands.default_permissions(mute_members=True)
    async def vcunmute(self, itx: discord.Interaction, member: discord.Member):
        await itx.response.defer(ephemeral=True)
        if member.voice:
            await member.edit(mute=False)
            await itx.followup.send(f"🔊 {member.mention} kann im Voice wieder sprechen.")
        else:
            await itx.followup.send("❌ Nutzer ist in keinem Voice-Kanal.")
async def setup(bot): await bot.add_cog(VcunmuteCog(bot))
