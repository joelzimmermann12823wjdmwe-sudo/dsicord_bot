import discord
from discord.ext import commands
from discord import ui, app_commands

# --- EINGABE-FENSTER (MODALS) ---

class WhitelistModal(ui.Modal, title="Whitelist Eintrag"):
    item_id = ui.TextInput(label="ID (User oder Rolle)", placeholder="Zahlen-ID hier einfügen...", required=True)
    item_type = ui.TextInput(label="Typ (user/role/link)", placeholder="user", required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        # Speichern in die Supabase Tabelle 'whitelist'
        self.bot.db.table("whitelist").insert({
            "guild_id": str(interaction.guild.id),
            "target_id": str(self.item_id.value),
            "type": str(self.item_type.value).lower()
        }).execute()
        await interaction.response.send_message(f"✅ `{self.item_id.value}` wurde zur Whitelist hinzugefügt.", ephemeral=True)

# --- DAS HAUPT-MENÜ (VIEW) ---

class SettingsView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.select(
        placeholder="Wähle eine Kategorie...",
        options=[
            discord.SelectOption(label="Rollen & Admin", emoji="🛡️", value="roles"),
            discord.SelectOption(label="Whitelist & Filter", emoji="📜", value="safety"),
            discord.SelectOption(label="Anti-Nuke Status", emoji="☢️", value="nuke")
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: ui.Select):
        embed = discord.Embed(title=f"Neon Settings: {select.values[0]}", color=discord.Color.from_rgb(0, 212, 255))
        
        # Wir passen die View dynamisch an (Buttons hinzufügen)
        self.clear_items()
        self.add_item(select) # Select-Menü behalten

        if select.values[0] == "roles":
            embed.description = "Klicke auf den Button, um die Admin-Rolle zu setzen."
            btn = ui.Button(label="Admin-Rolle setzen", style=discord.ButtonStyle.primary, custom_id="set_admin")
            # Logik für den Button-Klick:
            async def btn_callback(itn):
                await itn.response.send_message("Nutze bitte `!setadmin @Rolle` (Feature in Arbeit)", ephemeral=True)
            btn.callback = btn_callback
            self.add_item(btn)

        elif select.values[0] == "safety":
            embed.description = "Hier kannst du Einträge zur Whitelist hinzufügen."
            btn = ui.Button(label="+ Whitelist", style=discord.ButtonStyle.success)
            async def wl_callback(itn):
                await itn.response.send_modal(WhitelistModal(self.bot))
            btn.callback = wl_callback
            self.add_item(btn)

        await interaction.response.edit_message(embed=embed, view=self)

# --- DER COMMAND ---

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="settings", description="Zentrales Dashboard für Server-Einstellungen.")
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        embed = discord.Embed(
            title="NEON BOT | Konfigurations-Panel",
            description="Wähle einen Tab aus, um die Datenbank-Einstellungen für diesen Server anzupassen.",
            color=discord.Color.from_rgb(0, 212, 255)
        )
        embed.set_footer(text="Änderungen werden live in Supabase gespeichert.")
        
        view = SettingsView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Settings(bot))