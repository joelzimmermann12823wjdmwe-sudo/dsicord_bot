import discord
from discord.ext import commands
from helpers import send_discipline_dm

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.hybrid_command(name="ban", description="Bannt einen Nutzer vom Server.")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        reason_text = reason or "kein Grund angegeben"
        dm_success = await send_discipline_dm(member, ctx.guild, "gebannt", reason_text)
        try:
            await member.ban(reason=reason_text)
            message = f"✅ {member.mention} wurde gebannt. Grund: {reason_text}."
            if not dm_success:
                message += " Hinweis: DM konnte nicht zugestellt werden."
            await ctx.send(message)
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte, den Nutzer zu bannen.")
        except discord.HTTPException as exc:
            await ctx.send(f"❌ Fehler beim Bannen: {exc}")


async def setup(bot):
    await bot.add_cog(Ban(bot))
