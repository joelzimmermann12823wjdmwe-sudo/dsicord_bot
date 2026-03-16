import discord
from discord.ext import commands

class SyncFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fixsync")
    @commands.is_owner()
    async def fixsync(self, ctx):
        """Löscht alle lokalen Server-Befehle, um Dopplungen zu vermeiden."""
        # 1. Löscht alle Befehle, die NUR für diesen Server registriert sind
        self.bot.tree.clear_commands(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        
        # 2. Synchronisiert die globalen Befehle neu
        await self.bot.tree.sync()
        
        await ctx.send("✅ Server-Sync bereinigt! Starte dein Discord ggf. neu (STRG+R), damit die alten Befehle verschwinden.")

async def setup(bot):
    await bot.add_cog(SyncFix(bot))