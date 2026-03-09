import discord
from discord import app_commands
from discord.ext import commands

class KickCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="kick", description="Kickt einen Nutzer vom Server")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, itx: discord.Interaction, member: discord.Member, grund: str = "Kein Grund"):
        await itx.response.defer(ephemeral=True)
        try:
            await member.kick(reason=grund)
            await itx.followup.send(f"👢 {member.mention} wurde gekickt.")
        except:
            await itx.followup.send("❌ Fehler beim Kicken.")
async def setup(bot): await bot.add_cog(KickCog(bot))
