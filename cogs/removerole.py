import discord
from discord import app_commands
from discord.ext import commands

class RemoveroleCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="removerole", description="Nimmt einem Nutzer eine Rolle weg")
    @app_commands.default_permissions(manage_roles=True)
    async def removerole(self, itx: discord.Interaction, member: discord.Member, role: discord.Role):
        await itx.response.defer(ephemeral=True)
        try:
            await member.remove_roles(role)
            await itx.followup.send(f"✅ {role.name} wurde von {member.mention} entfernt.")
        except:
            await itx.followup.send("❌ Fehler: Ich kann diese Rolle nicht entfernen.")
async def setup(bot): await bot.add_cog(RemoveroleCog(bot))
