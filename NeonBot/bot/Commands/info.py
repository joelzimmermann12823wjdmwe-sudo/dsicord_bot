import discord
from discord.ext import commands
from discord import app_commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name        = "help",
        description = "Zeigt alle verfügbaren Commands des Neon Bots"
    )
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 Neon Bot — Hilfe", color=discord.Color.blurple())
        embed.add_field(
            name  = "🔨 Moderation",
            value = "`/ban` `/unban` `/kick`\n`/mute` `/unmute`\n`/warn` `/warns` `/clearwarns`\n`/clear` `/slowmode`",
            inline = True
        )
        embed.add_field(
            name  = "🛡️ AutoMod",
            value = "`/automod` `/addword` `/removeword`\n`/blacklist` `/setconsequences`\n`/verstösse` `/resetverstoesse`",
            inline = True
        )
        embed.add_field(
            name  = "🎫 Tickets",
            value = "`/ticketsetup` `/supportrolle`",
            inline = True
        )
        embed.add_field(
            name  = "⚙️ Einstellungen",
            value = "`/setlog` `/setwelcome` `/testwelcome`",
            inline = True
        )
        embed.add_field(
            name  = "ℹ️ Info",
            value = "`/help` `/botinfo`\n`/userinfo` `/serverinfo`\n`/avatar`",
            inline = True
        )
        embed.set_footer(text="Neon Bot • /help für alle Commands")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name        = "botinfo",
        description = "Zeigt technische Informationen über den Neon Bot"
    )
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Neon Bot — Info", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Eingeloggt als", value=str(self.bot.user),                             inline=True)
        embed.add_field(name="Server",         value=str(len(self.bot.guilds)),                      inline=True)
        embed.add_field(name="User gesamt",    value=str(sum(g.member_count or 0 for g in self.bot.guilds)), inline=True)
        embed.add_field(name="Ping",           value=f"{round(self.bot.latency * 1000)}ms",          inline=True)
        embed.add_field(name="discord.py",     value=discord.__version__,                            inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name        = "userinfo",
        description = "Zeigt detaillierte Informationen über einen User"
    )
    @app_commands.describe(user="Der User über den Infos angezeigt werden (leer = du selbst)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user  = user or interaction.user
        embed = discord.Embed(
            title = f"👤 {user}",
            color = user.color if user.color != discord.Color.default() else discord.Color.blurple()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID",          value=str(user.id),                                  inline=True)
        embed.add_field(name="Bot",         value="✅ Ja" if user.bot else "❌ Nein",              inline=True)
        embed.add_field(name="Nickname",    value=user.nick or "*Keiner*",                        inline=True)
        embed.add_field(name="Beigetreten", value=f"<t:{int(user.joined_at.timestamp())}:R>",     inline=True)
        embed.add_field(name="Registriert", value=f"<t:{int(user.created_at.timestamp())}:R>",   inline=True)
        roles = [r.mention for r in reversed(user.roles) if r != interaction.guild.default_role]
        embed.add_field(
            name   = f"Rollen ({len(roles)})",
            value  = " ".join(roles[:10]) + (" ..." if len(roles) > 10 else "") if roles else "*Keine*",
            inline = False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name        = "serverinfo",
        description = "Zeigt Informationen über diesen Server"
    )
    async def serverinfo(self, interaction: discord.Interaction):
        g     = interaction.guild
        embed = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="ID",         value=str(g.id),                                  inline=True)
        embed.add_field(name="Mitglieder", value=str(g.member_count),                        inline=True)
        embed.add_field(name="Channels",   value=str(len(g.channels)),                       inline=True)
        embed.add_field(name="Rollen",     value=str(len(g.roles)),                          inline=True)
        embed.add_field(name="Erstellt",   value=f"<t:{int(g.created_at.timestamp())}:R>",  inline=True)
        embed.add_field(name="Owner",      value=g.owner.mention if g.owner else "*?*",      inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name        = "avatar",
        description = "Zeigt den Avatar eines Users in voller Auflösung"
    )
    @app_commands.describe(user="Der User dessen Avatar angezeigt wird (leer = du selbst)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user  = user or interaction.user
        embed = discord.Embed(title=f"🖼️ Avatar: {user.display_name}", color=discord.Color.blurple())
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
