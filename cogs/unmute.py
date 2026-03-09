import discord
from discord import app_commands
from discord.ext import commands

class UnmuteCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="unmute", description="Hebt die Stummschaltung auf")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, itx: discord.Interaction, member: discord.Member):
        await itx.response.defer(ephemeral=True)
        try:
            await member.timeout(None)
            await itx.followup.send(f"🔊 {member.mention} kann wieder sprechen.")
        except:
            await itx.followup.send("❌ Fehler beim Entmuten.")
async def setup(bot): await bot.add_cog(UnmuteCog(bot))
