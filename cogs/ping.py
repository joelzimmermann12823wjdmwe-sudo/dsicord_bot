import discord
from discord import app_commands
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ping", description="Zeigt die aktuelle Latenz des Bots")
    async def ping(self, itx: discord.Interaction):
        await itx.response.defer(ephemeral=False)
        latenz = round(self.bot.latency * 1000)
        await itx.followup.send(f"🏓 Pong! Latenz: **{latenz}ms**")
async def setup(bot): await bot.add_cog(PingCog(bot))
