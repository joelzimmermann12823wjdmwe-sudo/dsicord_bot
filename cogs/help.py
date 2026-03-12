import discord
from discord.ext import commands
from discord import app_commands

class LinkButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Deine gewünschten Links
        self.add_item(discord.ui.Button(label="Website", style=discord.ButtonStyle.link, url="https://neon-bot-2026.vercel.app"))
        self.add_item(discord.ui.Button(label="Support", style=discord.ButtonStyle.link, url="https://neon-bot-2026.vercel.app/contact"))
        self.add_item(discord.ui.Button(label="Datenschutz", style=discord.ButtonStyle.link, url="https://neon-bot-2026.vercel.app/privacy"))
        self.add_item(discord.ui.Button(label="Nutzungsbedingungen", style=discord.ButtonStyle.link, url="https://neon-bot-2026.vercel.app/terms"))

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Detaillierte Übersicht aller Neon Bot Funktionen")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚡ Neon Bot | System-Dokumentation",
            description="Hier findest du eine vollständige Liste aller integrierten Module und Befehle. Nutze die Buttons unten für rechtliche Infos oder Support.",
            color=0x00ffff,
            timestamp=discord.utils.utcnow()
        )

        # --- KATEGORIE: MODERATION ---
        embed.add_field(
            name="🛡️ Moderation",
            value=(
                "`/ban` & `/unban`: Nutzer dauerhaft sperren oder entbannen.\n"
                "`/softban`: Kurzer Bann zum Löschen von Nachrichten.\n"
                "`/kick`: Nutzer vom Server kicken.\n"
                "`/mute` & `/unmute`: Nutzer im Textchat stummschalten.\n"
                "`/clear`: Eine bestimmte Anzahl an Nachrichten löschen.\n"
                "`/nuke`: **Setzt den kompletten Kanal zurück** (Löschen & Neuerstellen).\n"
                "`/slowmode`: Verzögerung für Nachrichten im Kanal einstellen.\n"
                "`/nick`: Den Nicknamen eines Nutzers ändern."
            ),
            inline=False
        )

        # --- KATEGORIE: ADMINISTRATION & CONFIG ---
        embed.add_field(
            name="⚙️ Administration & Schutz",
            value=(
                "`/automod`: Automatisches Moderations-System konfigurieren.\n"
                "`/link_filter`: Verhindert das Senden von unerwünschten Links.\n"
                "`/lock` & `/unlock`: Kanäle für alle Nutzer sperren/entsperren.\n"
                "`/whitelist`: Verwalte die Liste der vertrauenswürdigen Nutzer.\n"
                "`/settings`: Globale Bot-Einstellungen für diesen Server.\n"
                "`/logging`: Konfiguriere den Log-Kanal für Server-Events.\n"
                "`/welcome`: Setup für Willkommens- und Abschiedsnachrichten."
            ),
            inline=False
        )

        # --- KATEGORIE: ROLES & VOICE ---
        embed.add_field(
            name="🎭 Rollen & Sprachkanäle",
            value=(
                "`/addrole` & `/removerole`: Rollen an Nutzer vergeben oder entfernen.\n"
                "`/vckick`: Nutzer sofort aus einem Sprachkanal werfen.\n"
                "`/vcmute` & `/vcunmute`: Sprach-Stummschaltung verwalten."
            ),
            inline=False
        )

        # --- KATEGORIE: INFORMATION & LEVEL ---
        embed.add_field(
            name="📊 Info & Statistik",
            value=(
                "`/userinfo`: Zeigt Details über einen Nutzer an.\n"
                "`/serverinfo`: Statistiken und Infos zum aktuellen Server.\n"
                "`/avatar`: Zeigt das Profilbild eines Nutzers in groß.\n"
                "`/level_system`: Dein aktuelles Level und XP-Fortschritt.\n"
                "`/ping`: Zeigt die aktuelle Latenz zum Server an."
            ),
            inline=False
        )

        # --- KATEGORIE: SYSTEM ---
        embed.add_field(
            name="💻 System-Module",
            value=(
                "`/owner`: Exklusive Befehle für den Bot-Entwickler.\n"
                "`/status_bot`: Zeigt den aktuellen System-Status.\n"
                "`/test_cmd`: Internes Testmodul für Entwickler."
            ),
            inline=False
        )

        # Footer & Icons
        embed.set_footer(text="Neon Bot 2026 • High-End Discord Solutions", icon_url=self.bot.user.display_avatar.url)
        if interaction.user.display_avatar:
            embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed, view=LinkButtons())

async def setup(bot):
    await bot.add_cog(HelpCog(bot))