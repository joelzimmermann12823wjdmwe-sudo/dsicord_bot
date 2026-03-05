import discord
from discord.ext import commands
from supabase import create_client, Client
import os

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Config laden
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(member.guild.id)).execute()
        if not res.data: return
        
        cfg = res.data[0]['config']
        if not cfg.get("welcome") or not cfg.get("welcome_channel"): return

        channel = self.bot.get_channel(int(cfg["welcome_channel"]))
        if channel:
            msg = cfg.get("welcome_msg", "Willkommen auf dem Server, {user}!")
            # Platzhalter ersetzen
            msg = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
            
            embed = discord.Embed(description=msg, color=discord.Color.green())
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(content=member.mention, embed=embed)

async def setup(bot):
    await bot.add_cog(welcome(bot))