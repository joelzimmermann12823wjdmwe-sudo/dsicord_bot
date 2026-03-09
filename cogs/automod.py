import discord
from discord import app_commands
from discord.ext import commands

class AutomodCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="automod", description="Konfiguriert den Auto-Mod (Platzhalter)")
    @app_commands.default_permissions(administrator=True)
    async def automod(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=True)
        await itx.followup.send("🛡️ **Auto-Mod:** Hier wird bald der Wortfilter aktiviert!")
async def setup(bot): await bot.add_cog(AutomodCog(bot))
