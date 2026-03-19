import discord
from discord.ext import commands
from discord import app_commands
import os
import sys

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.developer_id = 1465263782258544680 # Deine ID

    async def is_owner(self, interaction: discord.Interaction):
        if interaction.user.id != self.developer_id:
            await interaction.response.send_message("❌ Dieser Befehl ist nur für den Bot-Entwickler.", ephemeral=True)
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
        
        await interaction.response.send_message(f"⚙️ Aktion `{action}` wird ausgeführt...", ephemeral=True)

        if action == "restart":
            os.execv(sys.executable, ['python'] + sys.argv)
        elif action == "shutdown":
            await self.bot.close()

    @owner_group.command(name="ban", description="User oder Server sperren")
    async def bot_ban(self, interaction: discord.Interaction, typ: str, id: str, grund: str = "Kein Grund angegeben"):
        if not await self.is_owner(interaction): return
        
        # Defer benutzen, um Timeouts zu verhindern!
        await interaction.response.defer(ephemeral=True)

        if self.bot.db:
            self.bot.db.table("bot_bans").upsert({
                "target_id": id,
                "type": typ,
                "reason": grund
            }).execute()
            await interaction.followup.send(f"✅ ID `{id}` ({typ}) wurde gesperrt.")
        else:
            await interaction.followup.send("❌ Keine Datenbankverbindung.")

    @owner_group.command(name="unban", description="User oder Server entsperren")
    async def bot_unban(self, interaction: discord.Interaction, id: str):
        if not await self.is_owner(interaction): return
        await interaction.response.defer(ephemeral=True)

        if self.bot.db:
            self.bot.db.table("bot_bans").delete().eq("target_id", id).execute()
            await interaction.followup.send(f"✅ ID `{id}` entsperrt.")

    @owner_group.command(name="list", description="Zeigt alle gebannten User und Server an")
    async def bot_ban_list(self, interaction: discord.Interaction):
        if not await self.is_owner(interaction): return
        await interaction.response.defer(ephemeral=True)

        if not self.bot.db:
            return await interaction.followup.send("❌ Keine Datenbank.")

        res = self.bot.db.table("bot_bans").select("*").execute()
        
        if not res.data:
            return await interaction.followup.send("ℹ️ Es sind aktuell keine IDs gesperrt.")

        embed = discord.Embed(title="🚫 Bot-Ban Liste", color=discord.Color.red())
        
        for entry in res.data:
            val = f"Typ: `{entry['type']}`\nGrund: {entry['reason']}"
            embed.add_field(name=f"ID: {entry['target_id']}", value=val, inline=False)

        await interaction.followup.send(embed=embed)

    # --- VERBESSERTER GLOBALER CHECK ---
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        # Wir prüfen nur, wenn es ein Command ist
        if interaction.type != discord.InteractionType.application_command:
            return

        # Owner darf immer alles
        if interaction.user.id == self.developer_id:
            return

        if not self.bot.db: return
        
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id) if interaction.guild else None

        # Nur eine gezielte Abfrage statt der ganzen Tabelle (schneller!)
        res = self.bot.db.table("bot_bans").select("target_id").or_(f"target_id.eq.{user_id},target_id.eq.{guild_id}").execute()

        if res.data:
            # Wenn der User oder Server in der Liste ist
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "🚫 **Zugriff verweigert.** Du oder dieser Server wurde global von der Bot-Nutzung ausgeschlossen. Fehler oder Bug? https://neon-bot-2026.vercel.app/contact", 
                    ephemeral=True
                )
            # Hier werfen wir einen Fehler, um die Ausführung des Commands zu stoppen
            raise app_commands.AppCommandError("Banned user/server attempted to use a command. https://neon-bot-2026.vercel.app/contact")

async def setup(bot):
    await bot.add_cog(Owner(bot))