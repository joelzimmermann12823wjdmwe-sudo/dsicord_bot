import discord
from discord.ext import commands
from typing import Optional

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="settings", description="Verwalte alle Bot-Einstellungen für diesen Server.")
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx, 
                        log_kanal: Optional[discord.TextChannel] = None, 
                        welcome_kanal: Optional[discord.TextChannel] = None, 
                        welcome_text: Optional[str] = None,
                        automod: Optional[bool] = None):
        
        guild_id = ctx.guild.id
        
        # Daten vorbereiten
        data = {"guild_id": guild_id}
        if log_kanal: data["log_channel_id"] = log_kanal.id
        if welcome_kanal: data["welcome_channel_id"] = welcome_kanal.id
        if welcome_text: data["welcome_message"] = welcome_text
        if automod is not None: data["automod_active"] = automod

        # In Supabase speichern (Upsert = Update oder Insert)
        self.bot.supabase.table("server_settings").upsert(data).execute()

        # Aktuelle Einstellungen abrufen für die Anzeige
        res = self.bot.supabase.table("server_settings").select("*").eq("guild_id", guild_id).execute()
        s = res.data[0]

        embed = discord.Embed(title="⚙️ Server-Einstellungen", color=discord.Color.blue())
        embed.add_field(name="Log-Kanal", value=f"<#{s['log_channel_id']}>" if s['log_channel_id'] else "Nicht gesetzt")
        embed.add_field(name="Willkommens-Kanal", value=f"<#{s['welcome_channel_id']}>" if s['welcome_channel_id'] else "Nicht gesetzt")
        embed.add_field(name="AutoMod", value="✅ Aktiv" if s['automod_active'] else "❌ Deaktiviert")
        embed.add_field(name="Willkommens-Nachricht", value=s['welcome_message'], inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Settings(bot))
