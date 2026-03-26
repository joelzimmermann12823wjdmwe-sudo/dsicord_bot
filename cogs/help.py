import discord
from discord.ext import commands


class HelpSelect(discord.ui.Select):
    def __init__(self, bot, mapping):
        self.bot = bot
        self.mapping = mapping

        options = [
            discord.SelectOption(
                label="Uebersicht",
                description="Zurueck zur Startseite",
                emoji="🏠",
            )
        ]

        for cog_name in mapping:
            if cog_name == "Owner":
                continue
            options.append(discord.SelectOption(label=cog_name, emoji="📁"))

        super().__init__(placeholder="Waehle eine Kategorie...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Uebersicht":
            embed = self.create_main_embed()
            await interaction.response.edit_message(embed=embed, view=self.view)
            return

        cog = self.bot.get_cog(self.values[0])
        if not cog:
            await interaction.response.send_message("Kategorie nicht gefunden.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📁 Kategorie: {self.values[0]}",
            description=f"Hier sind alle Befehle aus der Rubrik **{self.values[0]}**:",
            color=discord.Color.from_rgb(0, 212, 255),
        )

        entries = {}

        for command in cog.get_commands():
            if command.hidden:
                continue
            entries[command.name] = command.description or "Keine Beschreibung verfuegbar."

        for command in cog.get_app_commands():
            entries.setdefault(command.name, command.description or "Keine Beschreibung verfuegbar.")

        if not entries:
            embed.add_field(
                name="Keine Befehle",
                value="In dieser Kategorie sind aktuell keine Befehle registriert.",
                inline=False,
            )
        else:
            for name, description in sorted(entries.items()):
                embed.add_field(name=f"`/{name}`", value=description, inline=False)

        await interaction.response.edit_message(embed=embed, view=self.view)

    def create_main_embed(self):
        embed = discord.Embed(
            title="⚡ NEON BOT Hilfe-Zentrum",
            description=(
                "Willkommen beim Hilfe-Menue! Nutze das **Dropdown-Menue** unten, "
                "um dir die Befehle der einzelnen Kategorien anzeigen zu lassen.\n\n"
                "**Links:**\n"
                "🔗 [Support Server](https://discord.gg/deinlink)\n"
                "🌐 [Website](https://deinewebsite.de)"
            ),
            color=discord.Color.from_rgb(0, 212, 255),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Waehle eine Kategorie aus dem Menue unten!")
        return embed


class HelpView(discord.ui.View):
    def __init__(self, bot, mapping):
        super().__init__(timeout=60)
        self.add_item(HelpSelect(bot, mapping))


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Oeffnet das interaktive Hilfe-Menue")
    async def help(self, ctx):
        mapping = {}
        for cog_name, cog in self.bot.cogs.items():
            mapping[cog_name] = cog

        view = HelpView(self.bot, mapping)
        embed = discord.Embed(
            title="⚡ NEON BOT Hilfe-Zentrum",
            description=(
                "Willkommen beim Hilfe-Menue! Nutze das **Dropdown-Menue** unten, "
                "um dir die Befehle der einzelnen Kategorien anzeigen zu lassen."
            ),
            color=discord.Color.from_rgb(0, 212, 255),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
