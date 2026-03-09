import discord
from discord import app_commands
from discord.ext import commands

class OwnerCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="owner", description="Geheime Bot-Befehle")
    async def owner(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=True)
        # Pruefen, ob Nutzer Admin/Owner ist
        if not itx.user.guild_permissions.administrator:
            await itx.followup.send("❌ Du hast keine Rechte dafür.")
            return
        await itx.followup.send("👑 Owner-Panel: Der Bot läuft perfekt.")
async def setup(bot): await bot.add_cog(OwnerCog(bot))
