import discord
from discord import app_commands, ui
from discord.ext import commands


class WhitelistModal(ui.Modal, title="Zur Whitelist hinzufuegen"):
    item_id = ui.TextInput(label="ID (User oder Rolle)", placeholder="Zahlen-ID hier einfuegen...", required=True)
    item_type = ui.TextInput(label="Typ (user/role/link)", placeholder="user", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        if not self.bot.db:
            await interaction.response.send_message("❌ Datenbank nicht verfuegbar.", ephemeral=True)
            return

        try:
            self.bot.db.table("whitelist").insert(
                {
                    "guild_id": str(interaction.guild.id),
                    "target_id": str(self.item_id.value),
                    "type": str(self.item_type.value).lower(),
                }
            ).execute()
            await interaction.response.send_message(
                f"✅ `{self.item_id.value}` wurde zur Whitelist hinzugefuegt.",
                ephemeral=True,
            )
        except Exception as exc:
            await interaction.response.send_message(f"❌ Fehler: {exc}", ephemeral=True)


class AntiNukeLimitModal(ui.Modal, title="Anti-Nuke Limit"):
    limit = ui.TextInput(
        label="Max. Loeschungen pro Minute",
        placeholder="Standard: 10",
        required=True,
        min_length=1,
        max_length=2,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        if not self.limit.value.isdigit():
            await interaction.response.send_message("❌ Bitte gib eine Zahl ein.", ephemeral=True)
            return

        if not self.bot.db:
            await interaction.response.send_message("❌ Datenbank nicht verfuegbar.", ephemeral=True)
            return

        try:
            self.bot.db.table("guild_settings").upsert(
                {
                    "guild_id": str(interaction.guild.id),
                    "antinuke_limit": int(self.limit.value),
                }
            ).execute()
            await interaction.response.send_message(
                f"✅ Limit auf **{self.limit.value}** gesetzt.",
                ephemeral=True,
            )
        except Exception as exc:
            await interaction.response.send_message(f"❌ Fehler: {exc}", ephemeral=True)


class WelcomeTextModal(ui.Modal, title="Willkommens-Nachricht"):
    text = ui.TextInput(
        label="Begruessungstext",
        style=discord.TextStyle.long,
        default="Willkommen {user} auf {server}! Du bist unser {count}. Mitglied.",
        required=True,
    )
    image = ui.TextInput(label="Bild-URL (Optional)", placeholder="https://...", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        if not self.bot.db:
            await interaction.response.send_message("❌ Datenbank nicht verfuegbar.", ephemeral=True)
            return

        try:
            self.bot.db.table("guild_settings").upsert(
                {
                    "guild_id": str(interaction.guild.id),
                    "welcome_msg": self.text.value,
                    "welcome_image_url": self.image.value,
                }
            ).execute()
            await interaction.response.send_message(
                "✅ Willkommens-Text und Bild gespeichert!",
                ephemeral=True,
            )
        except Exception as exc:
            await interaction.response.send_message(f"❌ Fehler: {exc}", ephemeral=True)


class RoleSelect(ui.RoleSelect):
    def __init__(self, bot, db_field, label):
        self.bot = bot
        self.db_field = db_field
        super().__init__(placeholder=label, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        if not self.bot.db:
            await interaction.response.send_message("❌ Datenbank nicht verfuegbar.", ephemeral=True)
            return

        try:
            self.bot.db.table("guild_settings").upsert(
                {
                    "guild_id": str(interaction.guild.id),
                    self.db_field: str(role.id),
                }
            ).execute()
            await interaction.response.send_message(
                f"✅ Rolle {role.mention} fuer `{self.db_field}` gespeichert.",
                ephemeral=True,
            )
        except Exception as exc:
            await interaction.response.send_message(f"❌ Fehler: {exc}", ephemeral=True)


class ChannelSelect(ui.ChannelSelect):
    def __init__(self, bot, db_field, label):
        self.bot = bot
        self.db_field = db_field
        super().__init__(placeholder=label, min_values=1, max_values=1, channel_types=[discord.ChannelType.text])

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        if not self.bot.db:
            await interaction.response.send_message("❌ Datenbank nicht verfuegbar.", ephemeral=True)
            return

        try:
            self.bot.db.table("guild_settings").upsert(
                {
                    "guild_id": str(interaction.guild.id),
                    self.db_field: str(channel.id),
                }
            ).execute()
            await interaction.response.send_message(
                f"✅ Kanal {channel.mention} als `{self.db_field}` gesetzt.",
                ephemeral=True,
            )
        except Exception as exc:
            await interaction.response.send_message(f"❌ Fehler: {exc}", ephemeral=True)


class SettingsView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.select(
        placeholder="Waehle eine Kategorie...",
        options=[
            discord.SelectOption(label="Admin & Mod Rollen", emoji="🛡️", value="roles"),
            discord.SelectOption(label="Logs & Kanaele", emoji="📺", value="channels"),
            discord.SelectOption(label="Anti-Nuke & Whitelist", emoji="☢️", value="security"),
            discord.SelectOption(label="Willkommens-System", emoji="👋", value="welcome"),
        ],
    )
    async def select_category(self, interaction: discord.Interaction, select: ui.Select):
        value = select.values[0]
        titles = {
            "roles": "Admin & Mod Rollen",
            "channels": "Logs & Kanaele",
            "security": "Anti-Nuke & Whitelist",
            "welcome": "Willkommens-System",
        }
        embed = discord.Embed(
            title=f"Einstellungen: {titles.get(value, 'Uebersicht')}",
            color=discord.Color.from_rgb(0, 212, 255),
        )

        self.clear_items()
        self.add_item(select)

        if value == "roles":
            embed.description = "Lege fest, welche Rollen den Bot verwalten duerfen."
            self.add_item(RoleSelect(self.bot, "admin_role_id", "Admin-Rolle waehlen..."))
            self.add_item(RoleSelect(self.bot, "mod_role_id", "Mod-Rolle waehlen..."))

        elif value == "channels":
            embed.description = "Konfiguriere Log- und Bot-Kanaele."
            self.add_item(ChannelSelect(self.bot, "log_channel_id", "Log-Kanal waehlen..."))

        elif value == "security":
            embed.description = "Verwalte den Anti-Nuke Schutz und die Whitelist."
            btn_limit = ui.Button(label="Anti-Nuke Limit", style=discord.ButtonStyle.secondary, emoji="📊")
            btn_limit.callback = lambda inner_interaction: inner_interaction.response.send_modal(
                AntiNukeLimitModal(self.bot)
            )
            btn_wl = ui.Button(label="Whitelist hinzufuegen", style=discord.ButtonStyle.success, emoji="➕")
            btn_wl.callback = lambda inner_interaction: inner_interaction.response.send_modal(
                WhitelistModal(self.bot)
            )
            self.add_item(btn_limit)
            self.add_item(btn_wl)

        elif value == "welcome":
            embed.description = "Konfiguriere die Begruessung fuer neue Mitglieder."
            self.add_item(ChannelSelect(self.bot, "welcome_channel_id", "Willkommens-Kanal waehlen..."))
            self.add_item(RoleSelect(self.bot, "welcome_role_id", "Auto-Rolle waehlen..."))
            btn_text = ui.Button(label="Text & Bild anpassen", style=discord.ButtonStyle.primary, emoji="📝")
            btn_text.callback = lambda inner_interaction: inner_interaction.response.send_modal(
                WelcomeTextModal(self.bot)
            )
            self.add_item(btn_text)

        await interaction.response.edit_message(embed=embed, view=self)


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="settings", description="Das zentrale Kontrollzentrum fuer alle Bot-Einstellungen.")
    @app_commands.checks.has_permissions(administrator=True)
    async def settings(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="NEON BOT | Konfiguration",
            description="Waehle eine Kategorie aus dem Menue, um den Bot anzupassen.\nAlle Aenderungen werden sofort gespeichert.",
            color=discord.Color.from_rgb(0, 212, 255),
        )
        embed.set_footer(text=f"Server: {interaction.guild.name}")

        view = SettingsView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Settings(bot))
