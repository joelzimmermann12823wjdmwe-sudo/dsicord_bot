import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Löscht eine bestimmte Anzahl an Nachrichten mit Filtern.")
    @app_commands.describe(
        anzahl="Wie viele Nachrichten sollen geprüft werden?",
        filter="Welche Nachrichten sollen gelöscht werden?",
        user="Optional: Nur Nachrichten von diesem User löschen"
    )
    @app_commands.choices(filter=[
        app_commands.Choice(name="Alle Nachrichten", value="all"),
        app_commands.Choice(name="Nur Bots", value="bots"),
        app_commands.Choice(name="Nur User (keine Bots)", value="users"),
        app_commands.Choice(name="Nur Bilder/Anhänge", value="files"),
        app_commands.Choice(name="Nur Pins behalten", value="pins")
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self, 
        interaction: discord.Interaction, 
        anzahl: int, 
        filter: str = "all", 
        user: discord.Member = None
    ):
        # Sicherheits-Check: Nicht mehr als 100 auf einmal (Discord Limit/Performance)
        if anzahl > 100:
            anzahl = 100
        if anzahl < 1:
            return await interaction.response.send_message("❌ Bitte gib eine Zahl zwischen 1 und 100 an.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        def check(m):
            # Logik für die verschiedenen Filter
            if user and m.author.id != user.id:
                return False
            
            if filter == "bots":
                return m.author.bot
            elif filter == "users":
                return not m.author.bot
            elif filter == "files":
                return len(m.attachments) > 0
            elif filter == "pins":
                return not m.pinned
            return True # "all"

        try:
            deleted = await interaction.channel.purge(limit=anzahl, check=check)
            
            msg = f"✅ Erfolgreich **{len(deleted)}** Nachrichten gelöscht."
            if user: msg += f" (Filter: von {user.name})"
            if filter != "all": msg += f" (Modus: {filter})"

            await interaction.followup.send(msg)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Fehler beim Löschen: {e}")

async def setup(bot):
    await bot.add_cog(Clear(bot))