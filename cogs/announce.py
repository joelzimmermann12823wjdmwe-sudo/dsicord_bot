import re

import discord
from discord import app_commands, ui
from discord.ext import commands


class AnnounceModal(ui.Modal):
    def __init__(self, role_ids: str | None = None):
        super().__init__(title="Neon Bot | Ankündigung erstellen")
        self.role_ids = role_ids or ""

    titel = ui.TextInput(
        label="Überschrift",
        placeholder="z.B. Wartungsarbeiten oder neues Event",
        style=discord.TextStyle.short,
        required=True,
    )

    inhalt = ui.TextInput(
        label="Inhalt der Ankündigung",
        placeholder="Schreibe hier deinen Text...",
        style=discord.TextStyle.long,
        required=True,
        max_length=2000,
    )

    bild_url = ui.TextInput(
        label="Bild-URL (Optional)",
        placeholder="Link zu einem Bild (https://...)",
        style=discord.TextStyle.short,
        required=False,
    )

    links = ui.TextInput(
        label="Links unten (Optional)",
        placeholder="Website | https://example.com\nPartner-Server | https://discord.gg/example",
        style=discord.TextStyle.long,
        required=False,
        max_length=1000,
    )

    autor = ui.TextInput(
        label="Footer-Text / Autor (Optional)",
        placeholder="Dein Name, Team oder kurzer Footer-Text",
        style=discord.TextStyle.short,
        required=False,
    )

    @staticmethod
    def _format_links(raw_links: str) -> list[str]:
        formatted_links: list[str] = []

        for raw_line in raw_links.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if "|" in line:
                label, url = [part.strip() for part in line.split("|", 1)]
                if url.startswith(("http://", "https://")):
                    formatted_links.append(f"[{label}]({url})" if label else url)
                    continue

            formatted_links.append(line)

        return formatted_links

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        ping_content = ""
        if self.role_ids:
            role_ids = re.findall(r"\d{17,19}", self.role_ids)
            ping_roles = []
            for role_id in role_ids:
                role = interaction.guild.get_role(int(role_id)) if interaction.guild else None
                if role:
                    ping_roles.append(role.mention)

            if ping_roles:
                ping_content = " ".join(ping_roles)

        embed = discord.Embed(
            title=self.titel.value,
            description=self.inhalt.value,
            color=discord.Color.from_rgb(0, 212, 255),
        )

        image_url = self.bild_url.value.strip()
        if image_url.startswith(("http://", "https://")):
            embed.set_image(url=image_url)

        link_lines = self._format_links(self.links.value)
        if link_lines:
            embed.add_field(name="Links", value="\n".join(link_lines), inline=False)

        footer_prefix = self.autor.value.strip()
        embed.set_footer(text=f"{footer_prefix} | Neon Bot" if footer_prefix else "Neon Bot")
        embed.timestamp = discord.utils.utcnow()

        channel = interaction.channel or (interaction.guild.system_channel if interaction.guild else None)
        if channel is None:
            await interaction.followup.send(
                "⚠️ Kanal nicht gefunden. Die Ankündigung konnte nicht gesendet werden.",
                ephemeral=True,
            )
            return

        try:
            if ping_content:
                await channel.send(content=ping_content, embed=embed)
            else:
                await channel.send(embed=embed)

            await interaction.followup.send(
                "✅ Deine Ankündigung wurde erfolgreich veröffentlicht.",
                ephemeral=True,
            )
        except Exception as exc:
            await interaction.followup.send(
                "⚠️ Beim Senden der Ankündigung ist ein Fehler aufgetreten.",
                ephemeral=True,
            )
            raise exc


class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ankündigung",
        description="Erstellt eine Ankündigung mit optionalen Rollen-IDs zum Pingen.",
    )
    @app_commands.describe(rollen_ids="Optionale Rollen-IDs zum Pingen, getrennt mit Komma")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction, rollen_ids: str | None = None):
        await interaction.response.send_modal(AnnounceModal(role_ids=rollen_ids))


async def setup(bot):
    await bot.add_cog(Announce(bot))
