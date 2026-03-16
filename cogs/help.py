import discord
from discord.ext import commands
from discord import app_commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Zeigt eine Liste aller verfügbaren Befehle an.")
    async def help(self, ctx):
        # Embed Erstellung im Neon-Stil
        embed = discord.Embed(
            title="NEON BOT | Befehlsübersicht",
            description="Hier findest du alle Funktionen, die ich für deinen Server bereitstelle.",
            color=discord.Color.from_rgb(0, 212, 255) # Neon Blau
        )
        
        # --- KATEGORIE: MODERATION ---
        moderation_cmds = (
            "`/ban`, `/kick`, `/warn`, `/timeout`, `/softban`, `/mute`, `/unmute`, "
            "`/clear`, `/slowmode`, `/lock`, `/unlock`, `/vckick`, `/vcmute`, `/vcunmute`"
        )
        embed.add_field(name="🛡️ Moderation", value=moderation_cmds, inline=False)

        # --- KATEGORIE: TOOLS & UTILITY ---
        tools_cmds = (
            "`/ping`, `/avatar`, `/serverinfo`, `/userinfo`, `/status_bot`, `/help` "
        )
        embed.add_field(name="🛠️ Tools & Utility", value=tools_cmds, inline=False)

        # --- KATEGORIE: KONFIGURATION ---
        config_cmds = (
            "`/settings`, `/welcome`, `/logging`, `/automod`, `/link_filter`, `/whitelist`"
        )
        embed.add_field(name="⚙️ System & Konfiguration", value=config_cmds, inline=False)

        # --- KATEGORIE: ROLLEN ---
        role_cmds = (
            "`/addrole`, `/removerole`"
        )
        embed.add_field(name="🎭 Rollen-Management", value=role_cmds, inline=False)

        # --- LINKS AM ENDE ---
        links = (
            "🔗 [Website](https://neon-bot-2026.vercel.app/)\n"
            "⚖️ [Nutzungsbedingungen](https://neon-bot-2026.vercel.app/terms)\n"
            "🔒 [Datenschutz](https://neon-bot-2026.vercel.app/privacy)\n"
            "✉️ [Kontakt](https://neon-bot-2026.vercel.app/contact)"
        )
        embed.add_field(name="Wichtige Links", value=links, inline=False)

        # Footer mit Bot-Icon (falls vorhanden)
        embed.set_footer(text=f"Neon Bot 2026 | Angefordert von {ctx.author.display_name}", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))