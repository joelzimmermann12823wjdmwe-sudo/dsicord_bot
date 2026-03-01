import discord, datetime
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data, is_module_enabled


class Welcome(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def _send(self, member, guild):
        cfg   = load_data("config.json")
        ch_id = cfg.get(str(guild.id), {}).get("welcome_channel")
        if not ch_id: return
        ch = guild.get_channel(int(ch_id))
        if not ch: return
        e = discord.Embed(
            title       = f"👋 Willkommen auf {guild.name}!",
            description = f"Hey {member.mention}, schoen dass du hier bist!\nDu bist Mitglied **#{guild.member_count}**!",
            color       = discord.Color.blurple(),
            timestamp   = datetime.datetime.utcnow()
        )
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="Account erstellt", value=f"<t:{int(member.created_at.timestamp())}:R>")
        e.set_footer(text=f"Neon Bot • {guild.name}")
        try: await ch.send(embed=e)
        except: pass
        try:
            dm = discord.Embed(title=f"👋 Willkommen auf {guild.name}!", description=f"Hallo **{member.display_name}**!", color=discord.Color.blurple())
            if guild.icon: dm.set_thumbnail(url=guild.icon.url)
            await member.send(embed=dm)
        except: pass

    @app_commands.command(name="setwelcome", description="Setzt den Welcome-Channel und aktiviert das Modul")
    @app_commands.describe(channel="Welcome-Channel")
    @app_commands.default_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cfg = load_data("config.json"); gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["welcome_channel"] = str(channel.id)
        cfg[gid]["module_welcome"]  = True
        save_data("config.json", cfg)
        await interaction.response.send_message(f"✅ Welcome: {channel.mention} — **aktiv**!", ephemeral=True)

    @app_commands.command(name="testwelcome", description="Testet die Willkommensnachricht")
    @app_commands.default_permissions(administrator=True)
    async def testwelcome(self, interaction: discord.Interaction):
        await self._send(interaction.user, interaction.guild)
        await interaction.response.send_message("✅ Testnachricht gesendet!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not is_module_enabled(member.guild.id, "welcome"): return
        await self._send(member, member.guild)


async def setup(bot): await bot.add_cog(Welcome(bot))
