import discord
from discord import app_commands
from discord.ext import commands

class SoftbanCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="softban", description="Bannt und entbannt Nutzer sofort (löscht Chatverlauf)")
    @app_commands.default_permissions(ban_members=True)
    async def softban(self, itx: discord.Interaction, member: discord.Member):
        await itx.response.defer(ephemeral=True)
        try:
            await member.ban(reason="Softban", delete_message_days=7)
            await itx.guild.unban(member)
            await itx.followup.send(f"✅ {member.name} wurde ge-softbannt (Nachrichten gelöscht).")
        except:
            await itx.followup.send("❌ Fehler beim Softbannen.")
async def setup(bot): await bot.add_cog(SoftbanCog(bot))
