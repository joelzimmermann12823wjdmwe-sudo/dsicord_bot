import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client
import os

class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    async def get_cfg(self, guild_id):
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        return res.data[0]['config'] if res.data else {}

    async def save_cfg(self, guild_id, config):
        self.supabase.table("server_configs").upsert({"guild_id": str(guild_id), "config": config}).execute()

    settings_group = app_commands.Group(name="settings", description="Bot-Konfiguration")

    @settings_group.command(name="module", description="Module an/aus")
    @app_commands.choices(modul=[
        app_commands.Choice(name="AutoMod", value="automod"),
        app_commands.Choice(name="Welcome", value="welcome"),
        app_commands.Choice(name="Logging", value="logging")
    ])
    async def toggle(self, itx: discord.Interaction, modul: str, status: bool):
        cfg = await self.get_cfg(itx.guild.id)
        cfg[modul] = status
        await self.save_cfg(itx.guild.id, cfg)
        await itx.followup.send(f"✅ **{modul}** ist jetzt {'AN' if status else 'AUS'}.", ephemeral=True)

    @settings_group.command(name="setup_welcome", description="Willkommens-Kanal festlegen")
    async def welcome_setup(self, itx: discord.Interaction, kanal: discord.TextChannel):
        cfg = await self.get_cfg(itx.guild.id)
        cfg["welcome_channel"] = str(kanal.id)
        cfg["welcome"] = True
        await self.save_cfg(itx.guild.id, cfg)
        await itx.followup.send(f"✅ Willkommens-Kanal auf {kanal.mention} gesetzt!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(settings(bot))