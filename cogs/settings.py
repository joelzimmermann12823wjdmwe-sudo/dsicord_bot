import discord
from discord.ext import commands
from discord import ui, app_commands

# --- 1. MODALS (EINGABEFENSTER) ---

class WhitelistModal(ui.Modal, title="Zur Whitelist hinzufügen"):
    item_id = ui.TextInput(label="ID (User oder Rolle)", placeholder="Zahlen-ID hier einfügen...", required=True)
    item_type = ui.TextInput(label="Typ (user/role/link)", placeholder="user", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        self.bot.db.table("whitelist").insert({
            "guild_id": str(interaction.guild.id),
            "target_id": str(self.item_id.value),
            "type": str(self.item_type.value).lower()
        }).execute()
        await interaction.response.send_message(f"✅ `{self.item_id.value}` wurde zur Whitelist hinzugefügt.", ephemeral=True)

class AntiNukeLimitModal(ui.Modal, title="Anti-Nuke Limit"):
    limit = ui.TextInput(label="Max. Löschungen pro Minute", placeholder="Standard: 10", required=True, min_length=1, max_length=2)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        if not self.limit.value.isdigit():
            return await interaction.response.send_message("❌ Bitte gib eine Zahl ein.", ephemeral=True)
        
        self.bot.db.table("guild_settings").upsert({
            "guild_id": str(interaction.guild.id),
            "antinuke_limit": int(self.limit.value)
        }).execute()
        await interaction.response.send_message(f"✅ Limit auf **{self.limit.value}** gesetzt.", ephemeral=True)

class WelcomeTextModal(ui.Modal, title="Willkommens-Nachricht"):
    text = ui.TextInput(
        label="Begrüßungstext",
        style=discord.TextStyle.long,
        default="Willkommen {user} auf {server}! Du bist unser {count}. Mitglied.",
        required=True
    )
    image = ui.TextInput(label="Bild-URL (Optional)", placeholder="https://...", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        self.bot.db.table("guild_settings").upsert({
            "guild_id": str(interaction.guild.id),
            "welcome_text": self.text.value,
            "welcome_image_url": self.image.value
        }).execute()
        await interaction.response.send_message("✅ Willkommens-Text und Bild gespeichert!", ephemeral=True)

# --- 2. SELECT MENÜS (AUSWAHL) ---

class RoleSelect(ui.RoleSelect):
    def __init__(self, bot, db_field, label):
        self.bot = bot
        self.db_field = db_field
        super().__init__(placeholder=label, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        self.bot.db.table("guild_settings").upsert({
            "guild_id": str(interaction.guild.id),
            self.db_field: str(role.id)
        }).execute()
        await interaction.response.send_message(f"✅ Rolle {role.mention} für `{self.db_field}` gespeichert.", ephemeral=True)

class ChannelSelect(ui.ChannelSelect):
    def __init__(self, bot, db_field, label):
        self.bot = bot
        self.db_field = db_field
        super().__init__(placeholder=label, min_values=1, max_values=1, channel_types=[discord.ChannelType.text])

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        self.bot.db.table("guild_settings").upsert({
            "guild_id": str(interaction.guild.id),
            self.db_field: str(channel.id)
        }).execute()
        await interaction.response.send_message(f"✅ Kanal {channel.mention} als `{self.db_field}` gesetzt.", ephemeral=True)

# --- 3. DAS HAUPTMENÜ (VIEW) ---

class SettingsView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.select(
        placeholder="Wähle eine Kategorie...",
        options=[
            discord.SelectOption(label="Admin & Mod Rollen", emoji="🛡️", value="roles"),
            discord.SelectOption(label="Logs & Kanäle", emoji="📺", value="channels"),
            discord.SelectOption(label="Anti-Nuke & Whitelist", emoji="☢️", value="security"),
            discord.SelectOption(label="Willkommens-System", emoji="👋", value="welcome")
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: ui.Select):
        val = select.values[0]
        embed = discord.Embed(title=f"Einstellungen: {select.label}", color=discord.Color.from_rgb(0, 212, 255))
        
        self.clear_items()
        self.add_item(select) # Hauptmenü immer behalten

        if val == "roles":
            embed.description = "Lege fest, welche Rollen den Bot verwalten dürfen."
            self.add_item(RoleSelect(self.bot, "admin_role_id", "Admin-Rolle wählen..."))
            self.add_item(RoleSelect(self.bot, "mod_role_id", "Mod-Rolle wählen..."))

        elif val == "channels":
            embed.description = "Konfiguriere Log- und Bot-Kanäle."
            self.add_item(ChannelSelect(self.bot, "log_channel_id", "Log-Kanal wählen..."))

        elif val == "security":
            embed.description = "Verwalte den Anti-Nuke Schutz und die Whitelist."
            # Limit Button
            btn_limit = ui.Button(label="Anti-Nuke Limit", style=discord.ButtonStyle.secondary, emoji="📊")
            btn_limit.callback = lambda i: i.response.send_modal(AntiNukeLimitModal(self.bot))
            # Whitelist Button
            btn_wl = ui.Button(label="Whitelist hinzufügen", style=discord.ButtonStyle.success, emoji="➕")
            btn_wl.callback = lambda i: i.response.send_modal(WhitelistModal(self.bot))
            self.add_item(btn_limit)
            self.add_item(btn_wl)

        elif val == "welcome":
            embed.description = "Konfiguriere die Begrüßung für neue Mitglieder."
            self.add_item(ChannelSelect(self.bot, "welcome_channel_id", "Willkommens-Kanal wählen..."))
            self.add_item(RoleSelect(self.bot, "welcome_role_id", "Auto-Rolle wählen..."))
            # Text Button
            btn_text = ui.Button(label="Text & Bild anpassen", style=discord.ButtonStyle.primary, emoji="📝")
            btn_text.callback = lambda i: i.response.send_modal(WelcomeTextModal(self.bot))
            self.add_item(btn_text)

        await interaction.response.edit_message(embed=embed, view=self)

# --- 4. DER COMMAND ---

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="settings", description="Das zentrale Kontrollzentrum für alle Bot-Einstellungen.")
    @app_commands.checks.has_permissions(administrator=True)
    async def settings(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="NEON BOT | Konfiguration",
            description="Wähle eine Kategorie aus dem Menü, um den Bot anzupassen.\nAlle Änderungen werden sofort gespeichert.",
            color=discord.Color.from_rgb(0, 212, 255)
        )
        embed.set_footer(text=f"Server: {interaction.guild.name}")
        
        view = SettingsView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot))