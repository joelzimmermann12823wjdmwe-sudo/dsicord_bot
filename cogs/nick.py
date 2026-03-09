import discord
from discord import app_commands
from discord.ext import commands

class NickCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="nick", description="Ändert den Nicknamen eines Nutzers")
    @app_commands.default_permissions(manage_nicknames=True)
    async def nick(self, itx: discord.Interaction, member: discord.Member, neuer_name: str):
        await itx.response.defer(ephemeral=True)
        try:
            await member.edit(nick=neuer_name)
            await itx.followup.send(f"✅ Nickname von {member.name} geändert zu {neuer_name}.")
        except:
            await itx.followup.send("❌ Fehler: Ich kann den Nicknamen dieses Nutzers nicht ändern.")
async def setup(bot): await bot.add_cog(NickCog(bot))
