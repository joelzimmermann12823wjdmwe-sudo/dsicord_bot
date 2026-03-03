import discord
from discord import app_commands
from discord.ext import commands

class CLEARUSER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clearuser", description="Befehl: clearuser")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clearuser(self, interaction: discord.Interaction , user: discord.Member, anzahl: int = 10):
        try:
            def check(m): return m.author == user
        d = await interaction.channel.purge(limit=anzahl, check=check); await interaction.response.send_message(f'🧹 {len(d)} Nachrichten von {user.name} gelöscht.', ephemeral=True)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CLEARUSER(bot))