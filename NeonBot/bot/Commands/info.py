import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Alle Befehle des Neon Bots")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 Neon Bot — Hilfe", color=discord.Color.blurple())
        embed.add_field(name="🔨 Moderation",  value="`/ban` `/unban` `/kick`\n`/mute` `/unmute`\n`/warn` `/warns` `/clearwarns`\n`/clear` `/slowmode`", inline=True)
        embed.add_field(name="🛡️ AutoMod",     value="`/addword` `/removeword`\n`/blacklist`\n`/setconsequences`\n`/violations` `/resetviolations`", inline=True)
        embed.add_field(name="🎫 Tickets",     value="`/ticket-setup`", inline=True)
        embed.add_field(name="📋 Logging",     value="`/setlog`",       inline=True)
        embed.add_field(name="👋 Welcome",     value="`/setwelcome`\n`/testwelcome`", inline=True)
        embed.add_field(name="ℹ️ Info",        value="`/help` `/botinfo`\n`/userinfo` `/serverinfo`\n`/avatar`", inline=True)
        embed.set_footer(text="Neon Bot • Dein Moderations-Bot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="Infos ueber den Neon Bot")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Neon Bot", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Server",    value=str(len(self.bot.guilds)),                               inline=True)
        embed.add_field(name="User",      value=str(sum(g.member_count for g in self.bot.guilds)),       inline=True)
        embed.add_field(name="Ping",      value=f"{round(self.bot.latency * 1000)}ms",                   inline=True)
        embed.add_field(name="discord.py", value=discord.__version__,                                   inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Infos ueber einen User")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user  = user or interaction.user
        embed = discord.Embed(title=f"👤 {user}", color=user.color if user.color != discord.Color.default() else discord.Color.blurple())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID",          value=str(user.id),                                  inline=True)
        embed.add_field(name="Nickname",    value=user.nick or "Kein",                           inline=True)
        embed.add_field(name="Bot",         value="✅" if user.bot else "❌",                     inline=True)
        embed.add_field(name="Beigetreten", value=f"<t:{int(user.joined_at.timestamp())}:R>",    inline=True)
        embed.add_field(name="Registriert", value=f"<t:{int(user.created_at.timestamp())}:R>",  inline=True)
        roles = [r.mention for r in reversed(user.roles) if r != interaction.guild.default_role]
        embed.add_field(name=f"Rollen ({len(roles)})", value=" ".join(roles[:10]) or "Keine",   inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Infos ueber diesen Server")
    async def serverinfo(self, interaction: discord.Interaction):
        g     = interaction.guild
        embed = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="Mitglieder", value=str(g.member_count),                         inline=True)
        embed.add_field(name="Channels",   value=str(len(g.channels)),                        inline=True)
        embed.add_field(name="Rollen",     value=str(len(g.roles)),                           inline=True)
        embed.add_field(name="Owner",      value=g.owner.mention,                             inline=True)
        embed.add_field(name="Erstellt",   value=f"<t:{int(g.created_at.timestamp())}:R>",   inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Zeigt den Avatar eines Users")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user  = user or interaction.user
        embed = discord.Embed(title=f"🖼️ Avatar von {user.display_name}", color=discord.Color.blurple())
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
