import discord
from discord import app_commands
from discord.ext import commands

class AddroleCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="addrole", description="Gibt einem Nutzer eine Rolle")
    @app_commands.default_permissions(manage_roles=True)
    async def addrole(self, itx: discord.Interaction, member: discord.Member, role: discord.Role):
        await itx.response.defer(ephemeral=True)
        try:
            await member.add_roles(role)
            await itx.followup.send(f"✅ {member.mention} hat die Rolle {role.mention} erhalten.")
        except Exception:
            await itx.followup.send("❌ Fehler: Meine Rolle ist nicht hoch genug im Server, um diese Rolle zu vergeben.")
async def setup(bot): await bot.add_cog(AddroleCog(bot))
