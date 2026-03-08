import discord
from discord import app_commands
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Zeigt die Neon Bot Hilfe")
    async def help(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=True)
        await itx.response.defer(ephemeral=True)
        # Defer verhindert den "Anwendung reagiert nicht" Fehler
        await itx.response.defer(ephemeral=False)

        embed = discord.Embed(
            title="Neon Bot - Hilfemenue",
            description="Dein All-in-One Bot fuer Moderation, System und Tools.",
            color=discord.Color.from_rgb(0, 255, 255) # Neon Blau
        )

        embed.add_field(
            name="ðŸ›¡ï¸ Moderation (Admin only)",
            value="`/ban`, `/kick`, `/mute`, `/clear`, `/lock`, `/nuke`, `/slowmode` - Halte deinen Server sauber.",
            inline=False
        )

        embed.add_field(
            name="âš™ï¸ Verwaltung",
            value="`/settings`, `/automod`, `/welcome`, `/logging`, `/addrole` - Automatisiere deinen Server.",
            inline=False
        )

        embed.add_field(
            name="ðŸ› ï¸ Tools & Info",
            value="`/ping`, `/avatar`, `/userinfo`, `/serverinfo`, `/nick` - Nuetzliche Funktionen fuer jeden.",
            inline=False
        )

        embed.add_field(
            name="ðŸ”— Links",
            value="[Besuche unsere Website](https://neon-bot-2026.vercel.app/)",
            inline=False
        )

        embed.set_footer(text="Neon Bot 2026 | Sharded for 1000+ Servers")
        
        await itx.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(help_cog(bot))
