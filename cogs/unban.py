import discord
from discord import app_commands
from discord.ext import commands

class UnbanCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="unban", description="Entbannt einen Nutzer (Nutzer-ID erforderlich)")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, itx: discord.Interaction, user_id: str):
        await itx.response.defer(ephemeral=True)
        try:
            user = await self.bot.fetch_user(int(user_id))
            await itx.guild.unban(user)
            await itx.followup.send(f"✅ {user.name} wurde entbannt.")
        except:
            await itx.followup.send("❌ Fehler: Nutzer nicht gefunden oder nicht gebannt.")
async def setup(bot): await bot.add_cog(UnbanCog(bot))
