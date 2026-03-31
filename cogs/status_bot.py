import discord
from discord.ext import commands
import sys

class StatusBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="status_bot", description="Zeigt den aktuellen System-Status an.")
    async def status_bot(self, ctx):
        embed = discord.Embed(title="🤖 System-Status", color=discord.Color.green())
        embed.add_field(name="Serveranzahl", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Nutzeranzahl", value=f"{len(self.bot.users)}", inline=True)
        embed.add_field(name="Python Version", value=sys.version.split()[0], inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StatusBot(bot))
