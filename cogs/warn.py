import datetime

import discord
from discord.ext import commands


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="warn", description="Verwarnt ein Mitglied und sendet eine DM.")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, grund: str):
        if hasattr(self.bot, "db") and self.bot.db:
            try:
                self.bot.db.table("warns").insert(
                    {
                        "user_id": str(member.id),
                        "guild_id": str(ctx.guild.id),
                        "reason": grund,
                        "moderator_id": str(ctx.author.id),
                    }
                ).execute()
            except Exception as exc:
                print(f"DB-Fehler: {exc}")

        embed = discord.Embed(
            title="⚠️ Verwarnung erhalten",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.add_field(name="Grund", value=grund, inline=True)
        embed.add_field(name="Link zum Server", value=f"https://discord.com/channels/{ctx.guild.id}", inline=False)

        dm_sent = True
        try:
            await member.send(embed=embed)
        except Exception:
            dm_sent = False

        message = f"✅ **{member.name}** wurde verwarnt. {'(DM gesendet)' if dm_sent else '(DM fehlgeschlagen)'}"
        if ctx.interaction is not None:
            await ctx.interaction.response.send_message(message, ephemeral=True)
        else:
            await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Warn(bot))
