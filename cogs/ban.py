import discord
from discord import app_commands
from discord.ext import commands

class BanCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ban", description="Bannt einen Nutzer")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, itx: discord.Interaction, member: discord.Member, grund: str = "Kein Grund"):
        await itx.response.defer(ephemeral=True)
        try:
            await member.ban(reason=grund)
            await itx.followup.send(f"🔨 {member.name} wurde gebannt.")
        except:
            await itx.followup.send("❌ Fehler: Fehlende Rechte.")

async def setup(bot): await bot.add_cog(BanCog(bot))
