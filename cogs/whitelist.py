import discord
from discord.ext import commands

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='whitelist', description='Konfiguration für das whitelist-Modul.')
    @commands.has_permissions(administrator=True)
    async def cmd_whitelist(self, ctx):
        await ctx.send(f'⚙️ Das **whitelist** Setup-Menü wird hier zukünftig geöffnet. (Verknüpfung mit Datenbank steht aus).')

async def setup(bot):
    await bot.add_cog(Whitelist(bot))
