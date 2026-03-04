import discord
from discord import app_commands
from discord.ext import commands
from bot.utils.config_manager import is_enabled

class BAN(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @app_commands.command(name="ban", description="Bannt einen User")
    async def ban(self, interaction: discord.Interaction, user: discord.Member):
        if not is_enabled(interaction.guild.id, "moderation"):
            return await interaction.response.send_message("❌ Dieses Modul ist deaktiviert!", ephemeral=True)
        await user.ban()
        await interaction.response.send_message(f"🔨 {user.name} wurde gebannt.")

async def setup(bot): await bot.add_cog(BAN(bot))