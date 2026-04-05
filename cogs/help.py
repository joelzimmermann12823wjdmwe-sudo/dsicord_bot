from discord.ext import commands

from helpers import create_embed


HELP_CATEGORIES = [
    (
        "Moderation",
        "/ban, /kick, /softban, /unban, /mute, /unmute, /timeout, /warn, /warns, /clear, /lock, /unlock, /slowmode",
    ),
    (
        "Voice",
        "/vckick, /vcmute, /vcunmute",
    ),
    (
        "Rollen & Nutzer",
        "/addrole, /removerole, /nick, /resetnick, /avatar, /userinfo",
    ),
    (
        "Tools",
        "/poll, /say, /ankündigung, /invite",
    ),
    (
        "Infos",
        "/help, /ping, /serverinfo, /status_bot, /dbcheck",
    ),
    (
        "Bot-Team",
        "/owner, /fixsync, /test_cmd, /ban_server, /unban_server, /ban_user, /unban_user, /add_bot_admin, /remove_bot_admin, /add_bot_developer, /remove_bot_developer",
    ),
]

HELP_LINKS = [
    "Website: https://neon-bot-2026.vercel.app/",
    "Nutzungsbedingungen: https://neon-bot-2026.vercel.app/terms",
    "Datenschutz: https://neon-bot-2026.vercel.app/privacy",
    "Kontakt: https://neon-bot-2026.vercel.app/contact",
    "Support Discord: https://discord.gg/b5RetTqM",
]


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Listet alle verfügbaren Befehle auf.")
    async def help_command(self, ctx: commands.Context):
        embed = create_embed(
            title="📘 Hilfe",
            description="Hier findest du alle Befehle nach Kategorien sortiert.",
            footer="/help | !help",
        )

        for category_name, category_commands in HELP_CATEGORIES:
            embed.add_field(
                name=category_name,
                value=category_commands,
                inline=False,
            )

        embed.add_field(
            name="Links",
            value="\n".join(HELP_LINKS),
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
