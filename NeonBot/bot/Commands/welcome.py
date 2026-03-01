import discord
from discord.ext import commands
from discord import app_commands
import datetime
from Commands.helper import load_data, save_data

def is_enabled(guild_id, module):
    return load_data("config.json").get(str(guild_id), {}).get(f"module_{module}", False)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setwelcome", description="Setzt den Willkommens-Channel")
    @app_commands.default_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        config = load_data("config.json")
        gid = str(interaction.guild.id)
        if gid not in config: config[gid] = {}
        config[gid]["welcome_channel"] = str(channel.id)
        config[gid]["module_welcome"]  = True
        save_data("config.json", config)
        await interaction.response.send_message(f"✅ Willkommens-Channel: {channel.mention}", ephemeral=True)

    @app_commands.command(name="testwelcome", description="Testet die Willkommensnachricht")
    @app_commands.default_permissions(administrator=True)
    async def testwelcome(self, interaction: discord.Interaction):
        await self._send_welcome(interaction.user, interaction.guild)
        await interaction.response.send_message("✅ Testnachricht gesendet!", ephemeral=True)

    async def _send_welcome(self, member, guild):
        config  = load_data("config.json")
        ch_id   = config.get(str(guild.id), {}).get("welcome_channel")
        if not ch_id: return
        channel = guild.get_channel(int(ch_id))
        if not channel: return
        embed = discord.Embed(
            title=f"👋 Willkommen auf {guild.name}!",
            description=f"Hey {member.mention}, schoen dass du hier bist!\nDu bist Mitglied **#{guild.member_count}**!",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account erstellt", value=f"<t:{int(member.created_at.timestamp())}:R>")
        embed.set_footer(text=f"Neon Bot • {guild.name}")
        await channel.send(embed=embed)
        try:
            dm = discord.Embed(title=f"👋 Willkommen auf {guild.name}!", color=discord.Color.blurple(),
                               description=f"Hallo **{member.display_name}**!\nSchoen dass du unserem Server beigetreten bist!")
            if guild.icon: dm.set_thumbnail(url=guild.icon.url)
            await member.send(embed=dm)
        except (discord.Forbidden, discord.HTTPException):
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not is_enabled(member.guild.id, "welcome"): return
        await self._send_welcome(member, member.guild)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
