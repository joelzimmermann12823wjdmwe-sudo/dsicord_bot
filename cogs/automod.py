import discord
from discord.ext import commands

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="automod", description="Konfiguriert das AutoMod-System.")
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx, status: str):
        if status.lower() in ["an", "ein", "on", "enable"]:
            await ctx.send("🛡️ Automod wurde **aktiviert** (Platzhalter für Datenbank-Logik).")
        elif status.lower() in ["aus", "off", "disable"]:
            await ctx.send("🛡️ Automod wurde **deaktiviert**.")
        else:
            await ctx.send("Bitte benutze `/automod an` oder `/automod aus`.")

async def setup(bot):
    await bot.add_cog(Automod(bot))
