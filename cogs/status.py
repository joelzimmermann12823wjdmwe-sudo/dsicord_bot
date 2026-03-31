import discord
from discord import app_commands
from discord.ext import commands


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="show_settings",
        description="Zeigt die aktuell gespeicherten Server-Konfigurationen an.",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_settings(self, interaction: discord.Interaction):
        if not self.bot.db:
            await interaction.response.send_message(
                "❌ Datenbank-Verbindung nicht gefunden!",
                ephemeral=True,
            )
            return

        try:
            res = (
                self.bot.db.table("guild_settings")
                .select("*")
                .eq("guild_id", str(interaction.guild.id))
                .execute()
            )
        except Exception as exc:
            await interaction.response.send_message(f"❌ Datenbank-Fehler: {exc}", ephemeral=True)
            return

        if not res.data:
            await interaction.response.send_message(
                "⚠️ Keine Einstellungen fuer diesen Server gefunden. Nutze `/settings`!",
                ephemeral=True,
            )
            return

        data = res.data[0]
        guild = interaction.guild

        embed = discord.Embed(
            title=f"📊 Neon-Konfiguration fuer {guild.name}",
            description="Hier sind alle aktuell in der Datenbank hinterlegten Werte:",
            color=discord.Color.from_rgb(0, 212, 255),
        )

        admin_role = f"<@&{data.get('admin_role_id')}>" if data.get("admin_role_id") else "❌ Nicht gesetzt"
        mod_role = f"<@&{data.get('mod_role_id')}>" if data.get("mod_role_id") else "❌ Nicht gesetzt"
        embed.add_field(
            name="🛡️ Rollen",
            value=f"**Admin:** {admin_role}\n**Mod:** {mod_role}",
            inline=False,
        )

        log_channel = f"<#{data.get('log_channel_id')}>" if data.get("log_channel_id") else "❌ Nicht gesetzt"
        welcome_channel = (
            f"<#{data.get('welcome_channel_id')}>" if data.get("welcome_channel_id") else "❌ Nicht gesetzt"
        )
        embed.add_field(
            name="📺 Kanaele",
            value=f"**Logs:** {log_channel}\n**Welcome:** {welcome_channel}",
            inline=False,
        )

        anti_nuke_limit = data.get("antinuke_limit", 10)
        link_filter = "Aktiv" if data.get("link_filter_enabled", False) else "Deaktiviert"
        automod = "Aktiv" if data.get("automod_enabled", True) else "Deaktiviert"
        embed.add_field(
            name="☢️ Sicherheit",
            value=f"**Anti-Nuke:** {anti_nuke_limit}/Min.\n**Link-Filter:** {link_filter}\n**AutoMod:** {automod}",
            inline=False,
        )

        auto_role = f"<@&{data.get('welcome_role_id')}>" if data.get("welcome_role_id") else "❌ Keine"
        welcome_enabled = "Aktiv" if data.get("welcome_enabled", True) else "Deaktiviert"
        embed.add_field(
            name="👋 Willkommen",
            value=f"**Status:** {welcome_enabled}\n**Auto-Rolle:** {auto_role}",
            inline=False,
        )

        welcome_text = data.get("welcome_msg") or "Standard"
        if len(welcome_text) > 100:
            welcome_text = welcome_text[:97] + "..."
        embed.add_field(name="📝 Begruessungstext", value=f"```{welcome_text}```", inline=False)

        embed.set_footer(text="Nur du kannst diese Nachricht sehen.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Status(bot))
