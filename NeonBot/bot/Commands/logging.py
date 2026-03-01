import discord
from discord.ext import commands
from discord import app_commands
import datetime
from Commands.helper import load_data, save_data

def is_enabled(guild_id, module):
    return load_data("config.json").get(str(guild_id), {}).get(f"module_{module}", False)

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_ch(self, guild):
        if not is_enabled(guild.id, "logging"): return None
        ch_id = load_data("config.json").get(str(guild.id), {}).get("log_channel")
        return guild.get_channel(int(ch_id)) if ch_id else None

    @app_commands.command(name="setlog", description="Setzt den Log-Channel")
    @app_commands.default_permissions(administrator=True)
    async def setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        config = load_data("config.json")
        gid = str(interaction.guild.id)
        if gid not in config: config[gid] = {}
        config[gid]["log_channel"]    = str(channel.id)
        config[gid]["module_logging"] = True
        save_data("config.json", config)
        await interaction.response.send_message(f"✅ Log-Channel: {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = await self.log_ch(member.guild)
        if not ch: return
        e = discord.Embed(title="📥 Beigetreten", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="User",    value=f"{member.mention} (`{member.id}`)")
        e.add_field(name="Account", value=f"<t:{int(member.created_at.timestamp())}:R>")
        e.set_footer(text=f"Mitglieder: {member.guild.member_count}")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch = await self.log_ch(member.guild)
        if not ch: return
        e = discord.Embed(title="📤 Verlassen", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="User", value=f"{member} (`{member.id}`)")
        e.set_footer(text=f"Mitglieder: {member.guild.member_count}")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        ch = await self.log_ch(message.guild)
        if not ch: return
        e = discord.Embed(title="🗑️ Nachricht geloescht", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        e.add_field(name="Autor",   value=message.author.mention,                     inline=True)
        e.add_field(name="Channel", value=message.channel.mention,                    inline=True)
        e.add_field(name="Inhalt",  value=message.content[:1000] or "*Kein Text*",    inline=False)
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild: return
        if before.content == after.content: return
        ch = await self.log_ch(before.guild)
        if not ch: return
        e = discord.Embed(title="✏️ Nachricht bearbeitet", color=discord.Color.yellow(), timestamp=datetime.datetime.utcnow())
        e.add_field(name="Autor",   value=before.author.mention,             inline=True)
        e.add_field(name="Channel", value=before.channel.mention,            inline=True)
        e.add_field(name="Vorher",  value=before.content[:500] or "*Leer*",  inline=False)
        e.add_field(name="Nachher", value=after.content[:500] or "*Leer*",   inline=False)
        e.add_field(name="Link",    value=f"[Zur Nachricht]({after.jump_url})", inline=False)
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        ch = await self.log_ch(member.guild)
        if not ch: return
        if before.channel is None and after.channel:
            e = discord.Embed(title="🔊 Voice beigetreten", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
            e.add_field(name="User", value=member.mention); e.add_field(name="Channel", value=after.channel.name)
        elif before.channel and after.channel is None:
            e = discord.Embed(title="🔇 Voice verlassen", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
            e.add_field(name="User", value=member.mention); e.add_field(name="Channel", value=before.channel.name)
        elif before.channel and after.channel and before.channel != after.channel:
            e = discord.Embed(title="🔀 Voice gewechselt", color=discord.Color.yellow(), timestamp=datetime.datetime.utcnow())
            e.add_field(name="User", value=member.mention)
            e.add_field(name="Von", value=before.channel.name, inline=True)
            e.add_field(name="Nach", value=after.channel.name, inline=True)
        else: return
        await ch.send(embed=e)

async def setup(bot):
    await bot.add_cog(Logging(bot))
