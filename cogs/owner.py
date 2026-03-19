import discord
from discord.ext import commands
from discord import app_commands
import os
import sys

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.developer_id = 1465263782258544680 # Deine ID

    # --- HILFSFUNKTION: NUR DU DARFST DAS ---
    async def is_owner(self, interaction: discord.Interaction):
        if interaction.user.id != self.developer_id:
            await interaction.response.send_message("❌ Dieser Befehl ist nur für den Bot-Entwickler reserviert.", ephemeral=True)
            return False
        return True

    # --- GRUPPEN COMMAND: /OWNER ---
    owner_group = app_commands.Group(name="owner", description="Exklusive Entwickler-Befehle")

    @owner_group.command(name="system", description="Bot neustarten oder ausschalten")
    @app_commands.choices(action=[
        app_commands.Choice(name="Neustarten (Restart)", value="restart"),
        app_commands.Choice(name="Ausschalten (Shutdown)", value="shutdown")
    ])
    async def system_control(self, interaction: discord.Interaction, action: str):
        if not await self.is_owner(interaction): return

        if action == "restart":
            await interaction.response.send_message("🔄 Bot wird neu gestartet...", ephemeral=True)
            # Auf Hosting-Plattformen wie Render löst ein Exit-Code 1 oft einen Auto-Restart aus
            os.execv(sys.executable, ['python'] + sys.argv)
        
        elif action == "shutdown":
            await interaction.response.send_message("🛑 Bot wird heruntergefahren...", ephemeral=True)
            await self.bot.close()

    @owner_group.command(name="ban", description="Einen User oder Server vom Bot sperren")
    @app_commands.choices(typ=[
        app_commands.Choice(name="Benutzer (User)", value="user"),
        app_commands.Choice(name="Server (Guild)", value="guild")
    ])
    async def bot_ban(self, interaction: discord.Interaction, typ: str, id: str, grund: str = "Kein Grund angegeben"):
        if not await self.is_owner(interaction): return

        if self.bot.db:
            self.bot.db.table("bot_bans").upsert({
                "target_id": id,
                "type": typ,
                "reason": grund
            }).execute()
            
            msg = f"✅ {'Benutzer' if typ == 'user' else 'Server'} mit der ID `{id}` wurde vom Bot gesperrt.\n**Grund:** {grund}"
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Datenbank nicht erreichbar.", ephemeral=True)

    @owner_group.command(name="unban", description="Einen User oder Server entsperren")
    async def bot_unban(self, interaction: discord.Interaction, id: str):
        if not await self.is_owner(interaction): return

        if self.bot.db:
            self.bot.db.table("bot_bans").delete().eq("target_id", id).execute()
            await interaction.response.send_message(f"✅ ID `{id}` wurde erfolgreich entsperrt.", ephemeral=True)

    # --- GLOBALER CHECK ---
    # Dieser Teil prüft bei JEDER Interaktion, ob der User oder Server gebannt ist
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not self.bot.db: return
        
        # Prüfe User ID und Guild ID
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id) if interaction.guild else None

        # Datenbank-Check
        res = self.bot.db.table("bot_bans").select("*").execute()
        banned_ids = [item['target_id'] for item in res.data]

        if user_id in banned_ids or (guild_id and guild_id in banned_ids):
            # Falls gebannt, breche die Interaktion ab
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "🚫 Du oder dieser Server wurde von der Nutzung dieses Bots ausgeschlossen! Fehler oder Bug? https://neon-bot-2026.vercel.app/contact", 
                    ephemeral=True
                )
            return

async def setup(bot):
    await bot.add_cog(Owner(bot))