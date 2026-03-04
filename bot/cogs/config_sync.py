import discord
from discord.ext import commands
from bot.utils.config_manager import load_config, save_config

class ConfigSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        """Setzt den Welcome-Channel (wird ans Dashboard synchronisiert)"""
        save_config(ctx.guild.id, "welcome", {"enabled": True, "channel": str(channel.id)})
        await ctx.send(f"✅ Welcome-Channel auf {channel.mention} gesetzt und im Dashboard gespeichert!")

    @commands.command()
    async def automod(self, ctx, state: str):
        """Schaltet Automod via Command an/aus"""
        active = state.lower() == "on"
        save_config(ctx.guild.id, "automod", {"filter_badwords": active})
        await ctx.send(f"🛡️ Automod ist nun {'aktiviert' if active else 'deaktiviert'}.")

    # ... weitere: setlogs, setautorole, togglelevelsystem, setprefix
