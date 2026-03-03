import discord
from discord import app_commands
from discord.ext import commands

class BANNER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="banner", description="Befehl: banner")
    
    async def banner(self, interaction: discord.Interaction , user: discord.Member = None):
        try:
            u = user or interaction.user; await interaction.response.send_message(u.banner.url if u.banner else 'User hat keinen Banner.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BANNER(bot))