import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client
import os

class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    # Hilfsfunktion zum Laden/Speichern
    async def get_cfg(self, guild_id):
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        return res.data[0]['config'] if res.data else {}

    async def save_cfg(self, guild_id, config):
        self.supabase.table("server_configs").upsert({"guild_id": str(guild_id), "config": config}).execute()

    # HAUPT-COMMAND GRUPPE
    settings_group = app_commands.Group(name="settings", description="Das Haupt-Konfigurations-Menü")

    # 1. Module an/aus
    @settings_group.command(name="module", description="Module aktivieren oder deaktivieren")
    @app_commands.choices(modul=[
        app_commands.Choice(name="AutoMod", value="automod"),
        app_commands.Choice(name="Welcome-System", value="welcome"),
        app_commands.Choice(name="Logging", value="logging"),
        app_commands.Choice(name="Antilink", value="antilink")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_module(self, itx: discord.Interaction, modul: str, status: bool):
        cfg = await self.get_cfg(itx.guild.id)
        cfg[modul] = status
        await self.save_cfg(itx.guild.id, cfg)
        
        emoji = "✅" if status else "❌"
        await itx.response.send_message(f"{emoji} Modul **{modul}** wurde auf **{status}** gesetzt.", ephemeral=True)

    # 2. Welcome Setup
    @settings_group.command(name="welcome", description="Willkommens-System konfigurieren")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome(self, itx: discord.Interaction, kanal: discord.TextChannel = None, nachricht: str = None):
        cfg = await self.get_cfg(itx.guild.id)
        
        if kanal: cfg["welcome_channel"] = str(kanal.id)
        if nachricht: cfg["welcome_msg"] = nachricht
        
        await self.save_cfg(itx.guild.id, cfg)
        await itx.response.send_message(f"✅ Willkommens-Einstellungen gespeichert!\n**Kanal:** {kanal.mention if kanal else 'Unverändert'}\n**Text:** {nachricht if nachricht else 'Unverändert'}", ephemeral=True)

    # 3. Logging Setup
    @settings_group.command(name="logs", description="Logging-Kanal festlegen")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_logs(self, itx: discord.Interaction, kanal: discord.TextChannel):
        cfg = await self.get_cfg(itx.guild.id)
        cfg["log_channel"] = str(kanal.id)
        cfg["logging"] = True
        await self.save_cfg(itx.guild.id, cfg)
        await itx.response.send_message(f"✅ Logs werden jetzt in {kanal.mention} gesendet.", ephemeral=True)

    # 4. Übersicht anzeigen
    @settings_group.command(name="show", description="Zeigt alle aktuellen Einstellungen")
    async def show_all(self, itx: discord.Interaction):
        cfg = await self.get_cfg(itx.guild.id)
        embed = discord.Embed(title=f"⚙️ Konfiguration: {itx.guild.name}", color=discord.Color.blue())
        
        # Status-Checks
        def st(key): return "✅ AN" if cfg.get(key) else "❌ AUS"
        
        embed.add_field(name="🛡️ AutoMod", value=st("automod"), inline=True)
        embed.add_field(name="👋 Welcome", value=st("welcome"), inline=True)
        embed.add_field(name="📜 Logging", value=st("logging"), inline=True)
        
        if cfg.get("log_channel"):
            embed.add_field(name="📍 Log-Kanal", value=f"<#{cfg['log_channel']}>", inline=False)
        if cfg.get("welcome_msg"):
            embed.add_field(name="💬 Welcome-Text", value=f"```{cfg['welcome_msg']}```", inline=False)

        await itx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(settings(bot))