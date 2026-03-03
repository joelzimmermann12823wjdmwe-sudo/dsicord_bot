import discord
from discord import app_commands
from discord.ext import commands

class CLEAR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Befehl: clear")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction , anzahl: int = 10):
        try:
            d = await interaction.channel.purge(limit=anzahl); await interaction.response.send_message(f'🧹 {len(d)} Nachrichten gelöscht.', ephemeral=True)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CLEAR(bot))