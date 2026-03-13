import discord
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear", description="Löscht eine bestimmte Anzahl an Nachrichten.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, anzahl: int):
        if anzahl < 1 or anzahl > 100:
            return await ctx.send("❌ Bitte gib eine Zahl zwischen 1 und 100 ein.", ephemeral=True)
        
        gelöscht = await ctx.channel.purge(limit=anzahl + 1) # +1 um den Command-Aufruf mitzulöschen
        await ctx.send(f"✅ Erfolgreich **{len(gelöscht) - 1}** Nachrichten gelöscht.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Clear(bot))
