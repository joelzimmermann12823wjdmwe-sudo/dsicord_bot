import discord
from discord.ext import commands
from discord import ui, app_commands

# --- 1. DAS FORMULAR (MODAL) ---
class AnnounceModal(ui.Modal):
    def __init__(self, roles_to_ping):
        super().__init__(title="Neon Bot | Ankündigung erstellen")
        self.roles_to_ping = roles_to_ping # Liste der ausgewählten Rollen

    titel = ui.TextInput(
        label="Überschrift",
        placeholder="z.B. Wartungsarbeiten oder neues Event",
        style=discord.TextStyle.short,
        required=True
    )
    
    inhalt = ui.TextInput(
        label="Inhalt der Ankündigung",
        placeholder="Schreibe hier deinen Text... (Rollen-Erwähnungen funktionieren hier auch)",
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
        # Erstelle die Erwähnungen für außerhalb des Embeds
        ping_content = ""
        if self.roles_to_ping:
            ping_content = " ".join([role.mention for role in self.roles_to_ping])

        # Embed erstellen
        embed = discord.Embed(
            title=self.titel.value,
            description=self.inhalt.value,
            color=discord.Color.from_rgb(0, 212, 255) # Neon Blau
        )

        # Bild setzen
        if self.bild_url.value and self.bild_url.value.startswith("http"):
            embed.set_image(url=self.bild_url.value)

        # Footer / Autor
        if self.autor.value:
            embed.set_footer(text=f"Von: {self.autor.value} • {interaction.guild.name}")
        else:
            embed.set_footer(text=f"Ankündigung • {interaction.guild.name}")
        
        embed.timestamp = discord.utils.utcnow()

        # Nachricht im Kanal senden (Pings + Embed)
        await interaction.channel.send(content=ping_content, embed=embed)
        
        # Bestätigung nur für den Admin
        await interaction.response.send_message("✅ Ankündigung wurde erfolgreich veröffentlicht!", ephemeral=True)

# --- 2. DAS AUSWAHL-MENÜ (VIEW) ---
class AnnounceSetupView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.selected_roles = []

    # Rollen-Auswahlmenü (Mehrfachauswahl möglich)
    @ui.select(cls=ui.RoleSelect, placeholder="Wähle die Rollen zum Pingen aus...", min_values=0, max_values=5)
    async def select_roles(self, interaction: discord.Interaction, select: ui.RoleSelect):
        self.selected_roles = select.values
        await interaction.response.send_message(f"✅ {len(self.selected_roles)} Rollen zum Pingen vorgemerkt.", ephemeral=True)

    # Button zum Öffnen des Formulars
    @ui.button(label="Inhalt schreiben", style=discord.ButtonStyle.primary, emoji="✍️")
    async def open_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AnnounceModal(self.selected_roles))

# --- 3. DER COMMAND ---
class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announce", description="Erstellt eine Ankündigung mit Rollen-Pings.")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction):
        # Das Setup-Menü ist NUR für den Admin sichtbar (ephemeral)
        embed = discord.Embed(
            title="📢 Ankündigungs-Konfigurator",
            description=(
                "1. Wähle unten im Menü die Rollen aus, die gepingt werden sollen.\n"
                "2. Klicke dann auf den Button, um den Text zu schreiben.\n\n"
                "*Hinweis: Du kannst Rollen-Erwähnungen auch direkt in den Text schreiben.*"
            ),
            color=discord.Color.from_rgb(0, 212, 255)
        )
        view = AnnounceSetupView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Announce(bot))