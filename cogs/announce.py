import discord
from discord.ext import commands
from discord import ui, app_commands

# --- DAS FORMULAR (MODAL) ---
class AnnounceModal(ui.Modal):
    def __init__(self):
        # Der Titel des Fensters, das aufploppt
        super().__init__(title="Neue Ankündigung erstellen")

    # Eingabefelder
    titel = ui.TextInput(
        label="Überschrift",
        placeholder="z.B. Regelwerk Update oder Event-Ankündigung",
        style=discord.TextStyle.short,
        required=True
    )
    
    inhalt = ui.TextInput(
        label="Inhalt der Ankündigung",
        placeholder="Schreibe hier deinen Text rein...",
        style=discord.TextStyle.long,
        required=True,
        max_length=2000
    )

    bild_url = ui.TextInput(
        label="Bild-URL (Optional)",
        placeholder="https://beispiel.de/bild.png",
        style=discord.TextStyle.short,
        required=False
    )

    autor = ui.TextInput(
        label="Autor (Optional)",
        placeholder="Dein Name oder Team-Name",
        style=discord.TextStyle.short,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Das Embed erstellen
        embed = discord.Embed(
            title=self.titel.value,
            description=self.inhalt.value,
            color=discord.Color.from_rgb(0, 212, 255) # Neon Blau
        )

        # Bild hinzufügen, falls eine URL angegeben wurde
        if self.bild_url.value:
            # Einfacher Check, ob es ein Link ist
            if self.bild_url.value.startswith("http"):
                embed.set_image(url=self.bild_url.value)

        # Autor setzen (unten), falls angegeben
        if self.autor.value:
            embed.set_footer(text=f"Gesendet von: {self.autor.value}")
        else:
            embed.set_footer(text=f"Ankündigung • {interaction.guild.name}")

        # Zeitstempel hinzufügen
        embed.timestamp = discord.utils.utcnow()

        # Nachricht senden
        await interaction.response.send_message("✅ Ankündigung wurde gesendet!", ephemeral=True)
        await interaction.channel.send(embed=embed)

# --- DER COMMAND ---
class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announce", description="Öffnet ein Formular für eine professionelle Ankündigung.")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction):
        # Das Modal an den User senden
        await interaction.response.send_modal(AnnounceModal())

async def setup(bot):
    await bot.add_cog(Announce(bot))