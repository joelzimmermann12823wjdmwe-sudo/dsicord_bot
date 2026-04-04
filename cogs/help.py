import discord
from discord.ext import commands
from helpers import create_embed

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Listet alle verfügbaren Befehle auf.")
    async def help_command(self, ctx: commands.Context):
        embed = create_embed(
            title="📘 Hilfe",
            description="Hier findest du eine Übersicht über die verfügbaren Befehle.",
            footer="/help | !help",
        )
        embed.add_field(
            name="Moderation",
            value="/ban, /kick, /mute, /unmute, /timeout, /warn, /warns, /clear, /lock, /unlock, /slowmode",
            inline=False,
        )
        embed.add_field(
            name="Rollen & Nutzer",
            value="/addrole, /removerole, /nick, /resetnick, /avatar, /userinfo",
            inline=False,
        )
        embed.add_field(
            name="Sonstiges",
            value="/ping, /serverinfo, /invite, /poll, /say, /help, /dbcheck",
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="dbcheck", description="Testet die Datenbank-Verbindung.")
    async def dbcheck(self, ctx: commands.Context):
        try:
            perms = self.bot.storage.get_permissions()
            embed = create_embed(
                title="🗄️ Datenbank-Check",
                description="✅ Verbindung erfolgreich!",
                footer="Permissions geladen",
            )
            embed.add_field(name="Owner", value=str(len(perms.get("owner", []))), inline=True)
            embed.add_field(name="Admins", value=str(len(perms.get("admins", []))), inline=True)
            embed.add_field(name="Developers", value=str(len(perms.get("developers", []))), inline=True)
            embed.add_field(name="Gebannte Server", value=str(len(perms.get("banned_servers", []))), inline=True)
            embed.add_field(name="Gebannte User", value=str(len(perms.get("banned_users", []))), inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = create_embed(
                title="🗄️ Datenbank-Fehler",
                description=f"❌ Fehler: {str(e)}",
                footer="Prüfe .env und Supabase",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
