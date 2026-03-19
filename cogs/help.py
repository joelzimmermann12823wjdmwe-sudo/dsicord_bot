import discord
from discord.ext import commands
from discord import app_commands

# --- DAS DROPDOWN-MENÜ ---
class HelpSelect(discord.ui.Select):
    def __init__(self, bot, mapping):
        self.bot = bot
        self.mapping = mapping
        
        # Wir erstellen die Optionen für das Menü basierend auf den Cogs (Kategorien)
        options = [
            discord.SelectOption(
                label="Übersicht", 
                description="Zurück zur Startseite", 
                emoji="🏠"
            )
        ]
        
        # Wir fügen jede Cog (außer Owner-Befehle, falls gewünscht) hinzu
        for cog_name in mapping:
            if cog_name == "Owner": # Optional: Owner-Befehle verstecken
                continue
            options.append(discord.SelectOption(label=cog_name, emoji="📁"))

        super().__init__(placeholder="Wähle eine Kategorie...", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Wenn "Übersicht" gewählt wurde
        if self.values[0] == "Übersicht":
            embed = self.create_main_embed()
            await interaction.response.edit_message(embed=embed, view=self.view)
            return

        # Die gewählte Cog finden
        cog = self.bot.get_cog(self.values[0])
        if not cog:
            await interaction.response.send_message("Kategorie nicht gefunden.", ephemeral=True)
            return

        # Embed für die gewählte Kategorie erstellen
        embed = discord.Embed(
            title=f"📁 Kategorie: {self.values[0]}",
            description=f"Hier sind alle Befehle aus der Rubrik **{self.values[0]}**:",
            color=discord.Color.from_rgb(0, 212, 255)
        )

        for command in cog.get_commands():
            # Nur sichtbare Befehle anzeigen
            if not command.hidden:
                descr = command.description or "Keine Beschreibung verfügbar."
                embed.add_field(name=f"`/{command.name}`", value=descr, inline=False)

        await interaction.response.edit_message(embed=embed, view=self.view)

    def create_main_embed(self):
        embed = discord.Embed(
            title="⚡ NEON BOT Hilfe-Zentrum",
            description=(
                "Willkommen beim Hilfe-Menü! Nutze das **Dropdown-Menü** unten, "
                "um dir die Befehle der einzelnen Kategorien anzeigen zu lassen.\n\n"
                "**Links:**\n"
                "🔗 [Support Server](https://discord.gg/deinlink)\n"
                "🌐 [Website](https://deinewebsite.de)"
            ),
            color=discord.Color.from_rgb(0, 212, 255)
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Wähle eine Kategorie aus dem Menü unten!")
        return embed

# --- DIE VIEW (Container für das Menü) ---
class HelpView(discord.ui.View):
    def __init__(self, bot, mapping):
        super().__init__(timeout=60) # Menü deaktiviert sich nach 60 Sek Inaktivität
        self.add_item(HelpSelect(bot, mapping))

# --- DER COG ---
class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Öffnet das interaktive Hilfe-Menü")
    async def help(self, ctx):
        # Mapping aller Cogs erstellen
        mapping = {}
        for cog_name, cog in self.bot.cogs.items():
            mapping[cog_name] = cog

        # Start-Embed erstellen
        view = HelpView(self.bot, mapping)
        embed = discord.Embed(
            title="⚡ NEON BOT Hilfe-Zentrum",
            description=(
                "Willkommen beim Hilfe-Menü! Nutze das **Dropdown-Menü** unten, "
                "um dir die Befehle der einzelnen Kategorien anzeigen zu lassen."
            ),
            color=discord.Color.from_rgb(0, 212, 255)
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))