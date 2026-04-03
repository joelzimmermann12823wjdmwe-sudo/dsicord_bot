import discord
from discord.ext import commands

class SyncFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_developer(self):
        async def predicate(ctx):
            return ctx.author.id in self.bot.permissions.get("developers", [])
        return commands.check(predicate)

    @commands.hybrid_command(name="fixsync", description="Synchronisiert und bereinigt lokale Slash-Befehle.")
    @is_developer()
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