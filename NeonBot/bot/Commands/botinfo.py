import discord
from discord import app_commands
from discord.ext import commands

class BOTINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="botinfo", description="Befehl: botinfo")
    
    async def botinfo(self, interaction: discord.Interaction ):
        try:
            await interaction.response.send_message(f'🤖 **NeonBot**\nVers: 1.0.0\nPython: 3.14.3\nServer: {len(self.bot.guilds)}')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BOTINFO(bot))