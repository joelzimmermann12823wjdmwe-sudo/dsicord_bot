import discord
from discord import app_commands
from discord.ext import commands

class help_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Zeigt eine Übersicht aller verfügbaren Befehle")
    async def help(self, itx: discord.Interaction):
        # Timeout verhindern
        await itx.response.defer(ephemeral=False)

        embed = discord.Embed(
            title="✨ Neon Bot Hilfe-Menü",
            description="Hier findest du alle Befehle und deren Berechtigungen. Der Bot scannt alle Module automatisch!",
            color=discord.Color.blue()
        )

        # 1. MODERATION (Admin-Only)
        embed.add_field(
            name="🛡️ Moderation (Nur Admins)",
            value=(
                "`/ban` `/unban` `/softban` - Nutzer vom Server entfernen\n"
                "`/kick` `/vckick` - Nutzer kicken (Server/Voice)\n"
                "`/mute` `/unmute` `/vcmute` `/vcunmute` - Stummschalten\n"
                "`/clear` `/nuke` - Nachrichten massenweise löschen\n"
                "`/lock` `/unlock` - Kanäle sperren/entsperren\n"
                "`/slowmode` - Chat-Verzögerung einstellen"
            ),
            inline=False
        )

        # 2. VERWALTUNG & SYSTEM (Admin-Only)
        embed.add_field(
            name="⚙️ System & Verwaltung",
            value=(
                "`/settings` - Hauptmenü für alle Bot-Optionen\n"
                "`/automod` - Wortfilter und Schutz-System\n"
                "`/logging` - Log-Kanal Konfiguration\n"
                "`/welcome` - Willkommens-Nachrichten einstellen\n"
                "`/addrole` `/removerole` - Rollen zuweisen\n"
                "`/nick` - Nicknames ändern"
            ),
            inline=False
        )

        # 3. ALLGEMEIN (Für jeden nutzbar)
        embed.add_field(
            name="👥 Tools & Info (Jeder)",
            value=(
                "`/ping` - Latenz des Bots prüfen\n"
                "`/avatar` - Profilbild eines Nutzers anzeigen\n"
                "`/serverinfo` `/userinfo` - Details abrufen\n"
                "`/help` - Dieses Menü anzeigen"
            ),
            inline=False
        )

        # LINKS & WEBSITE
        embed.add_field(
            name="🔗 Nützliche Links",
            value=(
                "[Website](https://neon-bot-2026.vercel.app/)\n"
            ),
            inline=False
        )

        embed.set_footer(text="Neon Bot 2026 • Alle Module sind aktiv.")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await itx.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(help_command(bot))