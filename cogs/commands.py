import discord
from discord import app_commands
from discord.ext import commands
import datetime
import time

class AllCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = ["wort1", "wort2"] # Hier deine Blacklist

    # ==========================
    #   MODERATION & CHANNEL
    # ==========================
    @app_commands.command(name="ban", description="Permanent bannen")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.User, grund: str = "Kein Grund"):
        await interaction.guild.ban(user, reason=grund)
        await interaction.response.send_message(f"✅ Gebannt: {user.name}")

    @app_commands.command(name="clear", description="Nachrichten löschen")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, anzahl: int):
        deleted = await interaction.channel.purge(limit=min(anzahl, 100))
        await interaction.response.send_message(f"✅ {len(deleted)} Nachrichten gelöscht.", ephemeral=True)

    @app_commands.command(name="mute", description="Timeout setzen")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, dauer: int, grund: str = "Kein Grund"):
        until = discord.utils.utcnow() + datetime.timedelta(minutes=dauer)
        await user.timeout(until, reason=grund)
        await interaction.response.send_message(f"✅ Muted: {user.name} für {dauer} Min.")

    # ==========================
    #   ROLES & NICKNAME
    # ==========================
    @app_commands.command(name="addrole", description="Rolle vergeben")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole(self, interaction: discord.Interaction, user: discord.Member, rolle: discord.Role):
        await user.add_roles(rolle)
        await interaction.response.send_message(f"✅ Rolle {rolle.name} an {user.name} vergeben.")

    # ==========================
    #   INFO & TOOLS
    # ==========================
    @app_commands.command(name="ping", description="Latenz anzeigen")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="serverinfo", description="Server-Statistiken")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=f"Infos für {g.name}", color=discord.Color.blue())
        embed.add_field(name="Mitglieder", value=g.member_count)
        await interaction.response.send_message(embed=embed)

    # ==========================
    #   AUTOMOD (Listener)
    # ==========================
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        
        # Badwords Filter
        if any(w in message.content.lower() for w in self.bad_words):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, achte auf deine Wortwahl!", delete_after=3)

        # Caps Filter
        if len(message.content) > 15 and sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.75:
            await message.delete()

    # ==========================
    #   LOGGING & WELCOME
    # ==========================
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Hier später Logik für Willkommens-Kanal
        print(f"JOIN: {member.name}")

async def setup(bot):
    await bot.add_cog(AllCommands(bot))