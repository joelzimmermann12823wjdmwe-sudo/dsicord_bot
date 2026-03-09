import discord
from discord import app_commands
from discord.ext import commands

class NukeCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="nuke", description="Löscht den Kanal und erstellt ihn komplett neu")
    @app_commands.default_permissions(manage_channels=True)
    async def nuke(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=True)
        try:
            position = itx.channel.position
            new_channel = await itx.channel.clone(reason="Nuked")
            await itx.channel.delete()
            await new_channel.edit(position=position)
            await new_channel.send("💥 **Dieser Kanal wurde nuked!**")
        except:
            pass # Wenn der Kanal gelöscht ist, kann itx.followup fehlschlagen
async def setup(bot): await bot.add_cog(NukeCog(bot))
