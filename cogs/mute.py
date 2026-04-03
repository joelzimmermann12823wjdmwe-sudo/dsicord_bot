import discord
from discord.ext import commands
from helpers import send_discipline_dm

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_roles=True)
    @commands.hybrid_command(name="mute", description="Schaltet einen Nutzer stumm.")
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        reason_text = reason or "kein Grund angegeben"
        if not discord.utils.get(ctx.guild.roles, name="Muted"):
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, add_reactions=False)
        else:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        dm_success = await send_discipline_dm(member, ctx.guild, "stummgeschaltet", reason_text)
        try:
            await member.add_roles(muted_role, reason=reason_text)
            message = f"✅ {member.mention} wurde stummgeschaltet."
            if not dm_success:
                message += " Hinweis: DM konnte nicht zugestellt werden."
            await ctx.send(message)
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte, den Nutzer zu stummschalten.")
        except discord.HTTPException as exc:
            await ctx.send(f"❌ Fehler beim Stummschalten: {exc}")


async def setup(bot):
    await bot.add_cog(Mute(bot))
