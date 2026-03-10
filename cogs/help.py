import discord
from discord.ext import commands
import datetime

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Zeigt eine Übersicht aller verfügbaren Befehle.")
    async def help(self, ctx):
        e = discord.Embed(title="⚡ Neon Bot Hilfe", color=0x00ffff)
        e.add_field(name="🌐 Website", value="[Neon Bot Dashboard](https://neon-bot-2026.vercel.app/)")
        await ctx.send(embed=e)

async def setup(bot):
    await bot.add_cog(Help(bot))