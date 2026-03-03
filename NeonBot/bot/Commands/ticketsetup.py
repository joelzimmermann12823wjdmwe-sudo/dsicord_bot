import discord
from discord import app_commands
from discord.ext import commands

class TICKETSETUP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketsetup", description="Befehl: ticketsetup")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketsetup(self, interaction: discord.Interaction ):
        try:
            emb = discord.Embed(title='📩 Support-Tickets', description='Klicke auf den Button unten, um ein Ticket zu öffnen.'); await interaction.response.send_message(embed=emb)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TICKETSETUP(bot))