import discord
from discord.ext import commands
from discord import app_commands


class Info(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="help", description="Zeigt alle Commands des Neon Bots")
    async def help(self, interaction: discord.Interaction):
        e = discord.Embed(title="📖 Neon Bot — Hilfe", color=discord.Color.blurple())
        e.add_field(name="🔨 Moderation", value="`/ban` `/unban` `/kick`\n`/mute` `/unmute`\n`/warn` `/warns` `/clearwarns`\n`/clear` `/slowmode`", inline=True)
        e.add_field(name="🛡️ AutoMod",   value="`/automod`\n`/addword` `/removeword`\n`/blacklist`\n`/setconsequences`\n`/verstoesse`\n`/resetverstoesse`", inline=True)
        e.add_field(name="🎫 Tickets",   value="`/ticketsetup`\n`/supportrolle`", inline=True)
        e.add_field(name="⚙️ Setup",     value="`/setlog`\n`/setwelcome`\n`/testwelcome`", inline=True)
        e.add_field(name="ℹ️ Info",      value="`/help` `/botinfo`\n`/userinfo` `/serverinfo`\n`/avatar`", inline=True)
        e.set_footer(text="Neon Bot • Alle Commands sind Slash Commands (/)")
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="botinfo", description="Zeigt Informationen ueber den Neon Bot")
    async def botinfo(self, interaction: discord.Interaction):
        e = discord.Embed(title="🤖 Neon Bot", color=discord.Color.blurple())
        e.set_thumbnail(url=self.bot.user.display_avatar.url)
        e.add_field(name="Bot",        value=str(self.bot.user),                                     inline=True)
        e.add_field(name="Server",     value=str(len(self.bot.guilds)),                              inline=True)
        e.add_field(name="User",       value=str(sum(g.member_count or 0 for g in self.bot.guilds)), inline=True)
        e.add_field(name="Ping",       value=f"{round(self.bot.latency * 1000)}ms",                  inline=True)
        e.add_field(name="discord.py", value=discord.__version__,                                    inline=True)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="userinfo", description="Zeigt Informationen ueber einen User")
    @app_commands.describe(user="User (leer = du selbst)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user  = user or interaction.user
        color = user.color if user.color != discord.Color.default() else discord.Color.blurple()
        e     = discord.Embed(title=f"👤 {user}", color=color)
        e.set_thumbnail(url=user.display_avatar.url)
        e.add_field(name="ID",          value=str(user.id),                                inline=True)
        e.add_field(name="Bot",         value="✅ Ja" if user.bot else "❌ Nein",            inline=True)
        e.add_field(name="Nickname",    value=user.nick or "*Keiner*",                     inline=True)
        e.add_field(name="Beigetreten", value=f"<t:{int(user.joined_at.timestamp())}:R>",  inline=True)
        e.add_field(name="Registriert", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        roles = [r.mention for r in reversed(user.roles) if r != interaction.guild.default_role]
        e.add_field(name=f"Rollen ({len(roles)})", value=(" ".join(roles[:10]) + ("..." if len(roles) > 10 else "")) if roles else "*Keine*", inline=False)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="serverinfo", description="Zeigt Informationen ueber diesen Server")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        e = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
        if g.icon: e.set_thumbnail(url=g.icon.url)
        e.add_field(name="ID",         value=str(g.id),                                inline=True)
        e.add_field(name="Mitglieder", value=str(g.member_count),                      inline=True)
        e.add_field(name="Channels",   value=str(len(g.channels)),                     inline=True)
        e.add_field(name="Rollen",     value=str(len(g.roles)),                        inline=True)
        e.add_field(name="Owner",      value=g.owner.mention if g.owner else "*?*",    inline=True)
        e.add_field(name="Erstellt",   value=f"<t:{int(g.created_at.timestamp())}:R>", inline=True)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="avatar", description="Zeigt den Avatar eines Users in voller Groesse")
    @app_commands.describe(user="User (leer = du selbst)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        e    = discord.Embed(title=f"🖼️ {user.display_name}", color=discord.Color.blurple())
        e.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=e)


async def setup(bot): await bot.add_cog(Info(bot))
