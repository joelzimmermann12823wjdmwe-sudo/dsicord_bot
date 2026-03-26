import os
import sys

import discord
from discord import app_commands
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.developer_id = 1465263782258544680

    async def is_owner(self, interaction: discord.Interaction):
        if interaction.user.id != self.developer_id:
            await interaction.response.send_message(
                "❌ Dieser Befehl ist nur fuer den Bot-Entwickler.",
                ephemeral=True,
            )
            return False
        return True

    owner_group = app_commands.Group(name="owner", description="Exklusive Entwickler-Befehle")

    @owner_group.command(name="system", description="Bot neustarten oder ausschalten")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Neustarten (Restart)", value="restart"),
            app_commands.Choice(name="Ausschalten (Shutdown)", value="shutdown"),
        ]
    )
    async def system_control(self, interaction: discord.Interaction, action: str):
        if not await self.is_owner(interaction):
            return

        await interaction.response.send_message(
            f"⚙️ Aktion `{action}` wird ausgefuehrt...",
            ephemeral=True,
        )

        if action == "restart":
            os.execv(sys.executable, [sys.executable, *sys.argv])
        elif action == "shutdown":
            await self.bot.close()

    @owner_group.command(name="ban", description="User oder Server sperren")
    @app_commands.choices(
        typ=[
            app_commands.Choice(name="Benutzer (User)", value="user"),
            app_commands.Choice(name="Server (Guild)", value="guild"),
        ]
    )
    async def bot_ban(
        self,
        interaction: discord.Interaction,
        typ: str,
        id: str,
        grund: str = "Kein Grund angegeben",
    ):
        if not await self.is_owner(interaction):
            return

        await interaction.response.defer(ephemeral=True)

        if not self.bot.db:
            await interaction.followup.send("❌ Keine Datenbankverbindung.")
            return

        try:
            self.bot.db.table("bot_bans").upsert(
                {
                    "target_id": id,
                    "type": typ,
                    "reason": grund,
                }
            ).execute()

            status_msg = f"✅ ID `{id}` ({typ}) wurde gesperrt.\n**Grund:** {grund}"

            if typ == "guild":
                try:
                    guild_id_int = int(id)
                    guild = self.bot.get_guild(guild_id_int)
                    if guild:
                        await guild.leave()
                        status_msg += "\n🚪 Der Bot hat den Server verlassen."
                    else:
                        status_msg += "\nℹ️ Der Bot befindet sich nicht auf diesem Server."
                except Exception as exc:
                    status_msg += f"\n⚠️ Fehler beim Verlassen des Servers: {exc}"

            await interaction.followup.send(status_msg)
        except Exception as exc:
            await interaction.followup.send(f"❌ Datenbank-Fehler: {exc}")

    @owner_group.command(name="unban", description="User oder Server entsperren")
    async def bot_unban(self, interaction: discord.Interaction, id: str):
        if not await self.is_owner(interaction):
            return

        await interaction.response.defer(ephemeral=True)

        if not self.bot.db:
            await interaction.followup.send("❌ Keine Datenbankverbindung.")
            return

        try:
            self.bot.db.table("bot_bans").delete().eq("target_id", id).execute()
            await interaction.followup.send(
                f"✅ ID `{id}` entsperrt. Der Bot kann diesen Server nun wieder betreten."
            )
        except Exception as exc:
            await interaction.followup.send(f"❌ Datenbank-Fehler: {exc}")

    @owner_group.command(name="list", description="Zeigt alle gebannten User und Server an")
    async def bot_ban_list(self, interaction: discord.Interaction):
        if not await self.is_owner(interaction):
            return

        await interaction.response.defer(ephemeral=True)

        if not self.bot.db:
            await interaction.followup.send("❌ Keine Datenbank.")
            return

        res = self.bot.db.table("bot_bans").select("*").execute()
        if not res.data:
            await interaction.followup.send("ℹ️ Es sind aktuell keine IDs gesperrt.")
            return

        embed = discord.Embed(
            title="🚫 Bot-Ban Liste",
            description="Globale Sperrungen in der Datenbank",
            color=discord.Color.red(),
        )

        banned_users = [f"`{entry['target_id']}` - {entry['reason']}" for entry in res.data if entry["type"] == "user"]
        banned_guilds = [f"`{entry['target_id']}` - {entry['reason']}" for entry in res.data if entry["type"] == "guild"]

        embed.add_field(
            name="👤 Gesperrte Benutzer",
            value="\n".join(banned_users) if banned_users else "*Keine*",
            inline=False,
        )
        embed.add_field(
            name="🏢 Gesperrte Server",
            value="\n".join(banned_guilds) if banned_guilds else "*Keine*",
            inline=False,
        )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Owner(bot))
