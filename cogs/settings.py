import discord
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='settings', description='Konfiguration für das settings-Modul.')
    @commands.has_permissions(administrator=True)
    async def cmd_settings(self, ctx):
        await ctx.send(f'⚙️ Das **settings** Setup-Menü wird hier zukünftig geöffnet. (Verknüpfung mit Datenbank steht aus).')

async def setup(bot):
    await bot.add_cog(Settings(bot))
