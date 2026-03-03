import discord
from discord import app_commands
from discord.ext import commands

class NICK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nick", description="Befehl: nick")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(self, interaction: discord.Interaction , user: discord.Member, name: str):
        try:
            await user.edit(nick=name); await interaction.response.send_message(f'📝 Nickname von {user.name} zu {name} geändert.')
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NICK(bot))