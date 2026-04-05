import discord
from discord.ext import commands
from helpers import create_embed, send_discipline_dm

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="warn", description="Verwarnt einen Nutzer und speichert die Verwarnung.")
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "keine Angabe"):
        try:
            reason_text = reason or "keine Angabe"
            warn_count = self.bot.storage.add_warn(
                ctx.guild.id,
                member.id,
                ctx.author.id,
                reason_text,
            )
            dm_success = await send_discipline_dm(member, ctx.guild, "verwarnt", reason_text)
            embed = create_embed(
                title="⚠️ Nutzer verwarnt",
                description=f"{member.mention} wurde verwarnt.",
                footer=f"Warns gesamt: {warn_count}",
            )
            embed.add_field(name="Grund", value=reason_text, inline=False)
            if not dm_success:
                embed.add_field(name="Hinweis", value="DM konnte nicht zugestellt werden.", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = create_embed(
                title="❌ Fehler",
                description=f"Fehler beim Warnen: {str(e)}",
                footer="Versuche es später erneut",
            )
            await ctx.send(embed=embed)

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="warns", description="Zeigt die Verwarnungen eines Nutzers an.")
    async def warns(self, ctx: commands.Context, member: discord.Member = None):
        try:
            member = member or ctx.author
            warn_list = self.bot.storage.get_warns(ctx.guild.id, member.id)
            if not warn_list:
                embed = create_embed(
                    title="🔎 Verwarnungen",
                    description=f"{member.mention} hat keine Verwarnungen.",
                )
                await ctx.send(embed=embed)
                return

            lines = []
            for index, warn in enumerate(warn_list, start=1):
                moderator = ctx.guild.get_member(warn["moderator"])
                moderator_text = moderator.mention if moderator else f"<@{warn['moderator']}>"
                timestamp = warn["timestamp"].replace("T", " ").split(".")[0]
                lines.append(
                    f"**{index}.** {warn['reason']} — {moderator_text} ({timestamp} UTC)"
                )

            description = "\n".join(lines)
            if len(description) > 4000:
                description = description[:3990] + "…"

            embed = create_embed(
                title=f"🔎 Verwarnungen von {member.display_name}",
                description=description,
                footer=f"Warns gesamt: {len(warn_list)}",
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = create_embed(
                title="❌ Fehler",
                description=f"Fehler beim Laden der Warns: {str(e)}",
                footer="Versuche es später erneut",
            )
            await ctx.send(embed=embed)
