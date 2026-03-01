import discord, datetime
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data, is_module_enabled, get_log_channel_id


class Logging(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def _ch(self, guild):
        if not is_module_enabled(guild.id, "logging"): return None
        ch_id = get_log_channel_id(guild.id)
        return guild.get_channel(int(ch_id)) if ch_id else None

    @app_commands.command(name="setlog", description="Setzt den Log-Channel und aktiviert Logging")
    @app_commands.describe(channel="Log-Channel")
    @app_commands.default_permissions(administrator=True)
    async def setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cfg = load_data("config.json"); gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["log_channel"] = str(channel.id)
        cfg[gid]["module_logging"] = True
        save_data("config.json", cfg)
        await interaction.response.send_message(f"✅ Log-Channel: {channel.mention} — Logging **aktiv**!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = await self._ch(member.guild)
        if not ch: return
        e = discord.Embed(title="📥 Mitglied beigetreten", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="User",    value=f"{member.mention} (`{member.id}`)")
        e.add_field(name="Account", value=f"<t:{int(member.created_at.timestamp())}:R>")
        e.set_footer(text=f"Mitglieder: {member.guild.member_count}")
        try: await ch.send(embed=e)
        except: pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch = await self._ch(member.guild)
        if not ch: return
        e = discord.Embed(title="📤 Mitglied verlassen", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="User", value=f"{member} (`{member.id}`)")
        e.set_footer(text=f"Mitglieder: {member.guild.member_count}")
        try: await ch.send(embed=e)
        except: pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        ch = await self._ch(message.guild)
        if not ch: return
        e = discord.Embed(title="🗑️ Nachricht geloescht", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        e.add_field(name="Autor",   value=message.author.mention,                  inline=True)
        e.add_field(name="Channel", value=message.channel.mention,                 inline=True)
        e.add_field(name="Inhalt",  value=message.content[:1000] or "*Kein Text*", inline=False)
        try: await ch.send(embed=e)
        except: pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content: return
        ch = await self._ch(before.guild)
        if not ch: return
        e = discord.Embed(title="✏️ Nachricht bearbeitet", color=discord.Color.yellow(), timestamp=datetime.datetime.utcnow())
        e.add_field(name="Autor",   value=before.author.mention,            inline=True)
        e.add_field(name="Channel", value=before.channel.mention,           inline=True)
        e.add_field(name="Vorher",  value=before.content[:500] or "*Leer*", inline=False)
        e.add_field(name="Nachher", value=after.content[:500]  or "*Leer*", inline=False)
        e.add_field(name="Link",    value=f"[Zur Nachricht]({after.jump_url})", inline=False)
        try: await ch.send(embed=e)
        except: pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        ch = await self._ch(member.guild)
        if not ch: return
        if   before.channel is None and after.channel:
            e = discord.Embed(title="🔊 Voice beigetreten", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
            e.add_field(name="User",    value=member.mention)
            e.add_field(name="Channel", value=after.channel.name)
        elif before.channel and after.channel is None:
            e = discord.Embed(title="🔇 Voice verlassen", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
            e.add_field(name="User",    value=member.mention)
            e.add_field(name="Channel", value=before.channel.name)
        elif before.channel and after.channel and before.channel != after.channel:
            e = discord.Embed(title="🔀 Voice gewechselt", color=discord.Color.yellow(), timestamp=datetime.datetime.utcnow())
            e.add_field(name="User", value=member.mention)
            e.add_field(name="Von",  value=before.channel.name, inline=True)
            e.add_field(name="Nach", value=after.channel.name,  inline=True)
        else: return
        try: await ch.send(embed=e)
        except: pass


async def setup(bot): await bot.add_cog(Logging(bot))
