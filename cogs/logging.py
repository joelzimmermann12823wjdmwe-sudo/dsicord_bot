import discord
from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        res = self.bot.supabase.table("server_settings").select("log_channel_id").eq("guild_id", guild.id).execute()
        if res.data and res.data[0]['log_channel_id']:
            return guild.get_channel(res.data[0]['log_channel_id'])
        return None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        channel = await self.get_log_channel(message.guild)
        if channel:
            embed = discord.Embed(title="🗑️ Nachricht gelöscht", color=discord.Color.red())
            embed.add_field(name="Autor", value=message.author.mention)
            embed.add_field(name="Kanal", value=message.channel.mention)
            embed.add_field(name="Inhalt", value=message.content or "Kein Text (evtl. Bild)", inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        channel = await self.get_log_channel(before.guild)
        if channel:
            embed = discord.Embed(title="📝 Nachricht bearbeitet", color=discord.Color.orange())
            embed.add_field(name="Autor", value=before.author.mention)
            embed.add_field(name="Vorher", value=before.content, inline=False)
            embed.add_field(name="Nachher", value=after.content, inline=False)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))
