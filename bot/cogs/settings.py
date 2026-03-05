import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client
import os

class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    @app_commands.command(name="settings", description="Verwalte die Bot-Einstellungen für diesen Server")
    @app_commands.describe(modul="Welches Modul möchtest du ändern?", status="Ein- oder Ausschalten")
    @app_commands.choices(modul=[
        app_commands.Choice(name="AutoMod", value="automod"),
        app_commands.Choice(name="Welcome-System", value="welcome"),
        app_commands.Choice(name="Logging", value="logging")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def settings(self, itx: discord.Interaction, modul: str, status: bool):
        # 1. Aktuelle Config holen
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(itx.guild.id)).execute()
        config = res.data[0]['config'] if res.data else {}

        # 2. Update durchführen
        config[modul] = status

        # 3. Zurück nach Supabase (Upsert)
        self.supabase.table("server_configs").upsert({
            "guild_id": str(itx.guild.id),
            "config": config
        }).execute()

        status_text = "✅ Aktiviert" if status else "❌ Deaktiviert"
        embed = discord.Embed(
            title="Einstellungen aktualisiert",
            description=f"Das Modul **{modul.capitalize()}** wurde auf **{status_text}** gesetzt.",
            color=discord.Color.green() if status else discord.Color.red()
        )
        await itx.response.send_message(embed=embed)

    @app_commands.command(name="config", description="Zeigt die aktuellen Server-Einstellungen an")
    async def show_config(self, itx: discord.Interaction):
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(itx.guild.id)).execute()
        config = res.data[0]['config'] if res.data else {}

        embed = discord.Embed(title=f"Konfiguration für {itx.guild.name}", color=discord.Color.blue())
        
        # Module auflisten
        modules = ["automod", "welcome", "logging"]
        for m in modules:
            val = "✅ Aktiv" if config.get(m) else "❌ Inaktiv"
            embed.add_field(name=m.capitalize(), value=val, inline=True)

        await itx.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(settings(bot))