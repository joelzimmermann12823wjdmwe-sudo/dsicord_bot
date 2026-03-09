import discord
from discord import app_commands
from discord.ext import commands

class SlowmodeCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="slowmode", description="Setzt einen Slowmode im Kanal")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, itx: discord.Interaction, sekunden: int):
        await itx.response.defer(ephemeral=True)
        await itx.channel.edit(slowmode_delay=sekunden)
        await itx.followup.send(f"⏱️ Slowmode in diesem Kanal auf {sekunden} Sekunden gesetzt.")
async def setup(bot): await bot.add_cog(SlowmodeCog(bot))
