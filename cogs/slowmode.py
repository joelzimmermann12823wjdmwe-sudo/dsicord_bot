import discord
from discord.ext import commands

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slowmode", description="Setzt den Slowmode für den aktuellen Kanal.")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, sekunden: int):
        await ctx.channel.edit(slowmode_delay=sekunden)
        if sekunden == 0:
            await ctx.send("✅ Slowmode wurde deaktiviert.")
        else:
            await ctx.send(f"✅ Slowmode wurde auf **{sekunden} Sekunden** gesetzt.")

async def setup(bot):
    await bot.add_cog(Slowmode(bot))
