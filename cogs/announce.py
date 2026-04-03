import re
import discord
from discord.ext import commands
from discord import ui, app_commands

class AnnounceModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Neon Bot | Ankündigung erstellen")

    role_ids = ui.TextInput(
        label="Rollen-IDs zum Pingen (oben)",
        placeholder="123456789012345678, 876543210987654321",
        style=discord.TextStyle.short,
        required=False,
        max_length=2000
    )

    titel = ui.TextInput(
        label="Überschrift",
        placeholder="z.B. Wartungsarbeiten oder neues Event",
        style=discord.TextStyle.short,
        required=True
    )
    
    inhalt = ui.TextInput(
        label="Inhalt der Ankündigung",
        placeholder="Schreibe hier deinen Text...",
        style=discord.TextStyle.long,
        required=True,
        max_length=2000
    )

    bild_url = ui.TextInput(
        label="Bild-URL (Optional)",
        placeholder="Link zu einem Bild (https://...)",
        style=discord.TextStyle.short,
        required=False
    )

    autor = ui.TextInput(
        label="Autor / Signatur (Optional)",
        placeholder="Dein Name oder Team-Name",
        style=discord.TextStyle.short,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        ping_content = ""
        if self.role_ids.value:
            role_ids = re.findall(r"\d{17,19}", self.role_ids.value)
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
            color=discord.Color.from_rgb(0, 212, 255)
        )

        if self.bild_url.value and self.bild_url.value.startswith("http"):
            embed.set_image(url=self.bild_url.value)

        footer_text = f"Ankündigung • {interaction.guild.name}" if interaction.guild else "Neon Bot"
        if self.autor.value:
            embed.set_footer(text=f"Von: {self.autor.value} • {footer_text}")
        else:
            embed.set_footer(text=footer_text)

        embed.timestamp = discord.utils.utcnow()

        channel = interaction.channel or (interaction.guild.system_channel if interaction.guild else None)
        if channel is None:
            await interaction.followup.send(
                "⚠️ Kanal nicht gefunden. Die Ankündigung konnte nicht gesendet werden.",
                ephemeral=True
            )
            return

        try:
            if ping_content:
                await channel.send(content=ping_content, embed=embed)
            else:
                await channel.send(embed=embed)

            await interaction.followup.send(
                "✅ Deine Ankündigung wurde erfolgreich veröffentlicht.",
                ephemeral=True
            )
        except Exception as exc:
            await interaction.followup.send(
                "⚠️ Beim Senden der Ankündigung ist ein Fehler aufgetreten.",
                ephemeral=True
            )
            raise exc

class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ankündigung", description="Erstellt eine Ankündigung mit Rollen-ID zum Pingen.")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AnnounceModal())

async def setup(bot):
    await bot.add_cog(Announce(bot))