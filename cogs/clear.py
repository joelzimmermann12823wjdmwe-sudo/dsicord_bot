import discord
from discord import app_commands
from discord.ext import commands

class ClearCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="clear", description="Löscht massenhaft Nachrichten")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, itx: discord.Interaction, anzahl: int):
        await itx.response.defer(ephemeral=True)
        try:
            geloescht = await itx.channel.purge(limit=anzahl)
            await itx.followup.send(f"🗑️ {len(geloescht)} Nachrichten gelöscht.")
        except:
            await itx.followup.send("❌ Fehler: Nachrichten zu alt (Discord Limit: 14 Tage) oder keine Rechte.")
async def setup(bot): await bot.add_cog(ClearCog(bot))
