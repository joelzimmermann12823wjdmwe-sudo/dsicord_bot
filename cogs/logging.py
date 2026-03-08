import discord
from discord.ext import commands
from supabase import create_client, Client
import os

class logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    def get_config(self, guild_id):
        res = self.supabase.table("server_configs").select("config").eq("guild_id", str(guild_id)).execute()
        return res.data[0]['config'] if res.data else {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        cfg = self.get_config(message.guild.id)
        
        if cfg.get("logging") and cfg.get("log_channel"):
            channel = self.bot.get_channel(int(cfg.get("log_channel")))
            if channel:
                embed = discord.Embed(title="🗑️ Nachricht gelöscht", color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Autor", value=message.author.mention)
                embed.add_field(name="Kanal", value=message.channel.mention)
                embed.add_field(name="Inhalt", value=message.content or "Kein Text (evtl. Bild)", inline=False)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        cfg = self.get_config(before.guild.id)

        if cfg.get("logging") and cfg.get("log_channel"):
            channel = self.bot.get_channel(int(cfg.get("log_channel")))
            if channel:
                embed = discord.Embed(title="✏️ Nachricht bearbeitet", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Autor", value=before.author.mention)
                embed.add_field(name="Vorher", value=before.content, inline=False)
                embed.add_field(name="Nachher", value=after.content, inline=False)
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(logging(bot))
