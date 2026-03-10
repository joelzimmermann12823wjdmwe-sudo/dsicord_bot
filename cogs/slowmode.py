import discord
from discord.ext import commands
import datetime

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slowmode", description="Setzt eine Abklingzeit für Nachrichten in Sekunden.")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, sekunden: int):
        await ctx.channel.edit(slowmode_delay=sekunden)
        await ctx.send(f"⏳ Slowmode auf {sekunden} Sekunden gesetzt.")

async def setup(bot):
    await bot.add_cog(Slowmode(bot))