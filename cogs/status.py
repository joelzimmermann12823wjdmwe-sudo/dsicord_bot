import discord
from discord.ext import commands
from discord import app_commands

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="show_settings", description="Zeigt die aktuell gespeicherten Server-Konfigurationen an.")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_settings(self, interaction: discord.Interaction):
        if not self.bot.db:
            return await interaction.response.send_message("❌ Datenbank-Verbindung nicht gefunden!", ephemeral=True)

        # Daten aus Supabase abrufen
        res = self.bot.db.table("guild_settings").select("*").eq("guild_id", str(interaction.guild.id)).execute()
        
        if not res.data:
            return await interaction.response.send_message("⚠️ Keine Einstellungen für diesen Server gefunden. Nutze `/settings`!", ephemeral=True)

        data = res.data[0]
        guild = interaction.guild

        embed = discord.Embed(
            title=f"📊 Neon-Konfiguration für {guild.name}",
            description="Hier sind alle aktuell in der Datenbank hinterlegten Werte:",
            color=discord.Color.from_rgb(0, 212, 255)
        )

        # 🛡️ ROLLEN
        admin_role = f"<@&{data.get('admin_role_id')}>" if data.get('admin_role_id') else "❌ Nicht gesetzt"
        mod_role = f"<@&{data.get('mod_role_id')}>" if data.get('mod_role_id') else "❌ Nicht gesetzt"
        embed.add_field(name="🛡️ Rollen", value=f"**Admin:** {admin_role}\n**Mod:** {mod_role}", inline=False)

        # 📺 KANÄLE
        log_chan = f"<#{data.get('log_channel_id')}>" if data.get('log_channel_id') else "❌ Nicht gesetzt"
        wel_chan = f"<#{data.get('welcome_channel_id')}>" if data.get('welcome_channel_id') else "❌ Nicht gesetzt"
        embed.add_field(name="📺 Kanäle", value=f"**Logs:** {log_chan}\n**Welcome:** {wel_chan}", inline=False)

        # ☢️ SICHERHEIT
        limit = data.get('antinuke_limit', '10')
        embed.add_field(name="☢️ Anti-Nuke", value=f"**Limit:** {limit} Kanäle/Min.", inline=True)

        # 👋 WILLKOMMEN
        auto_role = f"<@&{data.get('welcome_role_id')}>" if data.get('welcome_role_id') else "❌ Keine"
        embed.add_field(name="👋 Willkommen", value=f"**Auto-Rolle:** {auto_role}", inline=True)
        
        welcome_text = data.get('welcome_text', 'Standard')
        if len(welcome_text) > 100: welcome_text = welcome_text[:97] + "..."
        embed.add_field(name="📝 Begrüßungstext", value=f"```{welcome_text}```", inline=False)

        embed.set_footer(text="Nur du kannst diese Nachricht sehen.")
        
        # Nur für den Admin sichtbar senden
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Status(bot))