import discord
from discord import app_commands
from discord.ext import commands

class LoggingCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="logging", description="Setzt den Log-Kanal (Platzhalter)")
    @app_commands.default_permissions(administrator=True)
    async def logging(self, itx: discord.Interaction, kanal: discord.TextChannel):
        await itx.response.defer(ephemeral=True)
        await itx.followup.send(f"📄 Logs werden bald in {kanal.mention} gesendet (Datenbank nötig)!")
async def setup(bot): await bot.add_cog(LoggingCog(bot))
