import discord
from discord.ext import commands
from helpers import send_discipline_dm

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(moderate_members=True)
    @commands.hybrid_command(name="timeout", description="Setzt einen Timeout für einen Nutzer.")
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: int, *, reason: str = None):
        reason_text = reason or "kein Grund angegeben"
        dm_success = await send_discipline_dm(member, ctx.guild, "in Timeout geschickt", reason_text, duration=duration)
        try:
            await member.timeout_for(duration * 60, reason=reason_text)
            message = f"✅ {member.mention} wurde für {duration} Minuten in Timeout geschickt."
            if not dm_success:
                message += " Hinweis: DM konnte nicht zugestellt werden."
            await ctx.send(message)
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte, den Nutzer in Timeout zu schicken.")
        except discord.HTTPException as exc:
            await ctx.send(f"❌ Fehler beim Timeout: {exc}")


async def setup(bot):
    await bot.add_cog(Timeout(bot))
