import discord
from discord import app_commands
from discord.ext import commands
from .helper import send_dm, save_json, load_json
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = load_json("warns.json")

    @app_commands.command(name="ban", description="Bannt einen User")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, itn: discord.Interaction, member: discord.Member, grund: str = "Kein Grund"):
        if member.top_role >= itn.user.top_role: return await itn.response.send_message("Hierarchie-Fehler!", ephemeral=True)
        await member.ban(reason=grund)
        await itn.response.send_message(f"✅ {member.name} gebannt.")

    @app_commands.command(name="warn", description="Verwarnt einen User")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, itn: discord.Interaction, member: discord.Member, grund: str):
        gid, uid = str(itn.guild.id), str(member.id)
        if gid not in self.warns: self.warns[gid] = {}
        if uid not in self.warns[gid]: self.warns[gid][uid] = []
        self.warns[gid][uid].append(grund)
        save_json("warns.json", self.warns)
        await itn.response.send_message(f"✅ Warn an {member.mention}. Gesamt: {len(self.warns[gid][uid])}")

    @app_commands.command(name="nick", description="Aendert Nickname")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(self, itn: discord.Interaction, member: discord.Member, name: str):
        await member.edit(nick=name)
        await itn.response.send_message(f"✅ Nick geaendert.")

    @app_commands.command(name="vckick", description="Kick aus Voice")
    @app_commands.checks.has_permissions(move_members=True)
    async def vckick(self, itn: discord.Interaction, member: discord.Member):
        if member.voice: await member.move_to(None); await itn.response.send_message("✅ Gekickt.")
        else: await itn.response.send_message("Nicht im Voice.", ephemeral=True)

async def setup(bot): await bot.add_cog(Moderation(bot))
