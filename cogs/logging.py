import discord
from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='logging', description='Konfiguration für das logging-Modul.')
    @commands.has_permissions(administrator=True)
    async def cmd_logging(self, ctx):
        await ctx.send(f'⚙️ Das **logging** Setup-Menü wird hier zukünftig geöffnet. (Verknüpfung mit Datenbank steht aus).')

async def setup(bot):
    await bot.add_cog(Logging(bot))
