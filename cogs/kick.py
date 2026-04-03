import discord
from discord.ext import commands
from helpers import send_discipline_dm

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.hybrid_command(name="kick", description="Kickt einen Nutzer vom Server.")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        reason_text = reason or "kein Grund angegeben"
        dm_success = await send_discipline_dm(member, ctx.guild, "gekickt", reason_text)
        try:
            await member.kick(reason=reason_text)
            message = f"✅ {member.mention} wurde gekickt. Grund: {reason_text}."
            if not dm_success:
                message += " Hinweis: DM konnte nicht zugestellt werden."
            await ctx.send(message)
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte, den Nutzer zu kicken.")
        except discord.HTTPException as exc:
            await ctx.send(f"❌ Fehler beim Kicken: {exc}")


async def setup(bot):
    await bot.add_cog(Kick(bot))
