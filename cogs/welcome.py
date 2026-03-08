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
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(member.guild.id)).execute()
        if not res.data: return
        cfg = res.data[0]['config']

        if cfg.get("welcome") and cfg.get("welcome_channel"):
            channel = self.bot.get_channel(int(cfg["welcome_channel"]))
            if channel:
                embed = discord.Embed(title="Willkommen!", description=f"Hallo {member.mention}, schön dass du da bist!", color=discord.Color.green())
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(welcome(bot))