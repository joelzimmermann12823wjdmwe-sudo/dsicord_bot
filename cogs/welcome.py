import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='welcome', description='Konfiguration für das welcome-Modul.')
    @commands.has_permissions(administrator=True)
    async def cmd_welcome(self, ctx):
        await ctx.send(f'⚙️ Das **welcome** Setup-Menü wird hier zukünftig geöffnet. (Verknüpfung mit Datenbank steht aus).')

async def setup(bot):
    await bot.add_cog(Welcome(bot))
