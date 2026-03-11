import discord
from discord.ext import commands
import traceback
import datetime

# Hier deine IDs eintragen (Oder später über Env-Variablen)
LOG_CHANNEL_ID = 1234567890  # ERSETZE MICH
ADMIN_ROLE_ID = 1234567890   # ERSETZE MICH

class StatusBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_count = 0

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        self.error_count += 1
        
        # Welches Modul hat den Fehler verursacht?
        cog_name = ctx.cog.qualified_name if ctx.cog else "Main/Unknown"
        
        # Den Fehler-Text formatieren
        error_trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        if len(error_trace) > 1000:
            error_trace = error_trace[:997] + "..."

        # Das Embed erstellen
        embed = discord.Embed(
            title="⚠️ Kritischer Systemfehler erkannt",
            color=0xff0000,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Modul", value=f"`{cog_name}`", inline=True)
        embed.add_field(name="Befehl", value=f"`{ctx.command}`", inline=True)
        embed.add_field(name="Fehlernummer", value=f"#{self.error_count}", inline=True)
        embed.add_field(name="Inhalt", value=f"```py\n{error}```", inline=False)
        embed.add_field(name="Traceback (Code-Ebene)", value=f"```py\n{error_trace}```", inline=False)
        
        embed.set_footer(text="Status: Wartend auf Fehlerbehebung...")

        # Kanal suchen und senden
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(content=f"<@&{ADMIN_ROLE_ID}> DRINGEND!", embed=embed)

    @commands.hybrid_command(name="reset_errors", description="Setzt den Fehlerzähler zurück.")
    @commands.has_permissions(administrator=True)
    async def reset_errors(self, ctx):
        self.error_count = 0
        await ctx.send("✅ Fehlerzähler wurde auf 0 gesetzt.")

async def setup(bot):
    await bot.add_cog(StatusBot(bot))
