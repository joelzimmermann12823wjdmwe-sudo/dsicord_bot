import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        if not self.bot.db:
            return

        try:
            res = self.bot.db.table("guild_settings").select("*").eq("guild_id", str(guild.id)).execute()
        except Exception:
            return

        if not res.data:
            return

        data = res.data[0]
        if not data.get("welcome_enabled", True):
            return

        role_id = data.get("welcome_role_id")
        if role_id:
            role = guild.get_role(int(role_id))
            if role:
                try:
                    await member.add_roles(role, reason="Neon Auto-Role")
                except Exception:
                    pass

        channel_id = data.get("welcome_channel_id")
        if not channel_id:
            return

        channel = guild.get_channel(int(channel_id))
        if channel is None:
            return

        raw_text = data.get("welcome_msg") or "Willkommen {user} auf {server}!"
        formatted_text = (
            raw_text.replace("{user}", member.mention)
            .replace("{server}", guild.name)
            .replace("{count}", str(guild.member_count))
        )

        embed = discord.Embed(
            title="👋 Ein neues Mitglied!",
            description=formatted_text,
            color=discord.Color.from_rgb(0, 212, 255),
        )

        image_url = data.get("welcome_image_url")
        if image_url and image_url.startswith("http"):
            embed.set_image(url=image_url)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id} | Wir sind jetzt {guild.member_count} Mitglieder")

        try:
            await channel.send(content=member.mention, embed=embed)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Welcome(bot))
