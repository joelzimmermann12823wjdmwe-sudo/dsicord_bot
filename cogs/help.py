import discord
from discord import app_commands
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Zeigt alle Befehle und Infos zum Neon Bot")
    async def help(self, itx: discord.Interaction):
        # Erstes Defer: Kauft 15 Minuten Zeit gegen den Timeout-Fehler
        await itx.response.defer(ephemeral=False)

        embed = discord.Embed(
            title="✨ Neon Bot - Hilfe & Übersicht",
            description="Dein Bot fuer Moderation, Verwaltung und Tools auf ueber 1.000 Servern.",
            color=discord.Color.blue()
        )

        # Kategorien basierend auf deinen Dateien
        embed.add_field(
            name="🛡️ Moderation (Admin)",
            value="`/ban`, `/kick`, `/mute`, `/clear`, `/lock`, `/nuke`, `/slowmode`",
            inline=False
        )

        embed.add_field(
            name="⚙️ System & Verwaltung",
            value="`/settings`, `/automod`, `/welcome`, `/logging`, `/addrole`",
            inline=False
        )

        embed.add_field(
            name="🛠️ Tools & Info",
            value="`/ping`, `/avatar`, `/userinfo`, `/serverinfo`, `/nick`",
            inline=False
        )

        # Website Link
        embed.add_field(
            name="🔗 Website",
            value="[https://neon-bot-2026.vercel.app/](https://neon-bot-2026.vercel.app/)",
            inline=False
        )

        embed.set_footer(text="Neon Bot 2026 | Sharding aktiv")
        
        # Antwort senden (WICHTIG: followup nutzen nach defer!)
        await itx.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(help_cog(bot))