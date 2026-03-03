import discord
from discord import app_commands
from discord.ext import commands

class MEMBERCOUNT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="membercount", description="Befehl: membercount")
    
    async def membercount(self, interaction: discord.Interaction ):
        try:
            await interaction.response.send_message(f'👥 Aktuelle Mitgliederzahl: **{interaction.guild.member_count}**')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MEMBERCOUNT(bot))