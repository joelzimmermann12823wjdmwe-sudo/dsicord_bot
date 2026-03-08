import discord
from discord.ext import commands
from supabase import create_client, Client
import os

class automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return

        # 1. Config aus Supabase laden
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(message.guild.id)).execute()
        if not res.data: return
        
        config = res.data[0]['config']
        if not config.get("automod"): return # Abbrechen wenn AutoMod deaktiviert ist

        # 2. Filter-Logik (Beispiel: SchimpfwÃ¶rter)
        bad_words = ["idiot", "noob"] # Erweitere diese Liste nach Belieben
        if any(word in message.content.lower() for word in bad_words):
            await message.delete()
            await message.channel.send(f"âš ï¸ {message.author.mention}, achte auf deine Wortwahl!", delete_after=3)

async def setup(bot):
    await bot.add_cog(automod(bot))
