import discord
from discord import app_commands
from discord.ext import commands
from bot.utils.config_manager import get_config, is_module_enabled

class AUTOMOD(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        
        # Prüfen ob Automod im Dashboard aktiviert ist
        cfg = get_config(message.guild.id).get("automod", {})
        if not cfg.get("enabled"): return

        banned_words = cfg.get("words", [])
        for word in banned_words:
            if word.lower() in message.content.lower():
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, dieses Wort ist verboten!", delete_after=3)
                break

async def setup(bot): await bot.add_cog(AUTOMOD(bot))