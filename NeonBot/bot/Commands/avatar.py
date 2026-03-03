import discord
from discord import app_commands
from discord.ext import commands

class AVATAR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Befehl: avatar")
    
    async def avatar(self, interaction: discord.Interaction , user: discord.Member = None):
        try:
            u = user or interaction.user; emb = discord.Embed(title=f'Avatar von {u.name}'); emb.set_image(url=u.avatar.url); await interaction.response.send_message(embed=emb)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AVATAR(bot))