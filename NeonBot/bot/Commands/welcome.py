import discord
import datetime
from discord.ext import commands
from discord import app_commands
from Commands.helper import load_data, save_data, is_module_enabled

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _send_welcome(self, member, guild):
        cfg   = load_data("config.json")
        ch_id = cfg.get(str(guild.id), {}).get("welcome_channel")
        if not ch_id: return
        ch = guild.get_channel(int(ch_id))
        if not ch: return
        embed = discord.Embed(
            title       = f"👋 Willkommen auf {guild.name}!",
            description = f"Hey {member.mention}, schön dass du hier bist!\nDu bist Mitglied **#{guild.member_count}**!",
            color       = discord.Color.blurple(),
            timestamp   = datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account erstellt", value=f"<t:{int(member.created_at.timestamp())}:R>")
        embed.set_footer(text=f"Neon Bot • {guild.name}")
        try: await ch.send(embed=embed)
        except: pass
        # DM an neues Mitglied
        try:
            dm = discord.Embed(
                title       = f"👋 Willkommen auf {guild.name}!",
                description = f"Hallo **{member.display_name}**!\nSchön dass du unserem Server beigetreten bist!",
                color       = discord.Color.blurple()
            )
            if guild.icon: dm.set_thumbnail(url=guild.icon.url)
            await member.send(embed=dm)
        except (discord.Forbidden, discord.HTTPException):
            pass

    @app_commands.command(
        name        = "setwelcome",
        description = "Setzt den Willkommens-Channel und aktiviert das Welcome-Modul"
    )
    @app_commands.describe(channel="Der Channel in dem Willkommensnachrichten gepostet werden")
    @app_commands.default_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cfg = load_data("config.json")
        gid = str(interaction.guild.id)
        if gid not in cfg: cfg[gid] = {}
        cfg[gid]["welcome_channel"] = str(channel.id)
        cfg[gid]["module_welcome"]  = True
        save_data("config.json", cfg)
        await interaction.response.send_message(
            f"✅ Willkommens-Channel: {channel.mention} — Welcome-Modul **aktiviert**!", ephemeral=True
        )

    @app_commands.command(
        name        = "testwelcome",
        description = "Testet die Willkommensnachricht mit deinem eigenen Account"
    )
    @app_commands.default_permissions(administrator=True)
    async def testwelcome(self, interaction: discord.Interaction):
        await self._send_welcome(interaction.user, interaction.guild)
        await interaction.response.send_message("✅ Testnachricht gesendet!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not is_module_enabled(member.guild.id, "welcome"): return
        await self._send_welcome(member, member.guild)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
