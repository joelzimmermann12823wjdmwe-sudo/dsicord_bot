import discord
from discord import app_commands
from discord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="welcome", description="Setzt den Willkommens-Kanal (Platzhalter)")
    @app_commands.default_permissions(administrator=True)
    async def welcome(self, itx: discord.Interaction, kanal: discord.TextChannel):
        await itx.response.defer(ephemeral=True)
        await itx.followup.send(f"👋 Willkommensnachrichten werden bald in {kanal.mention} gesendet (Datenbank nötig)!")
async def setup(bot): await bot.add_cog(WelcomeCog(bot))
