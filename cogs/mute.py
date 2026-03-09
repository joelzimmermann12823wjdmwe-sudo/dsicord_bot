import discord
from discord import app_commands
from discord.ext import commands
import datetime

class MuteCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="mute", description="Schaltet einen Nutzer temporär stumm (Timeout)")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, itx: discord.Interaction, member: discord.Member, minuten: int):
        await itx.response.defer(ephemeral=True)
        try:
            duration = datetime.timedelta(minutes=minuten)
            await member.timeout(duration)
            await itx.followup.send(f"🔇 {member.mention} wurde für {minuten} Minuten stummgeschaltet.")
        except:
            await itx.followup.send("❌ Fehler beim Stummschalten.")
async def setup(bot): await bot.add_cog(MuteCog(bot))
