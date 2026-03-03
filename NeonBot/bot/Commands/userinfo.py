import discord
from discord import app_commands
from discord.ext import commands

class USERINFO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Befehl: userinfo")
    
    async def userinfo(self, interaction: discord.Interaction , user: discord.Member = None):
        try:
            u = user or interaction.user; await interaction.response.send_message(f'👤 **User:** {u.name}\n🆔 **ID:** {u.id}\n📅 **Beigetreten:** {u.joined_at.strftime("%Y-%m-%d")}')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(USERINFO(bot))