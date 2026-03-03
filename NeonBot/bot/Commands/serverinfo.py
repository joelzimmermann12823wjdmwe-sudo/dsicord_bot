import discord
from discord import app_commands
from discord.ext import commands

class SERVERINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Befehl: serverinfo")
    
    async def serverinfo(self, interaction: discord.Interaction ):
        try:
            g = interaction.guild; emb = discord.Embed(title=g.name); emb.add_field(name='Mitglieder', value=g.member_count); emb.add_field(name='ID', value=g.id); await interaction.response.send_message(embed=emb)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SERVERINFO(bot))