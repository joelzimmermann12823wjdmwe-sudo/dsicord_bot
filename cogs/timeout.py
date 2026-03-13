import discord
from discord.ext import commands
import datetime

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="timeout", description="Versetzt einen Benutzer in den Timeout (Mute).")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minuten: int, *, grund: str = "Kein Grund angegeben"):
        try:
            dauer = datetime.timedelta(minutes=minuten)
            await member.timeout(dauer, reason=grund)
            await ctx.send(f"✅ **{member.display_name}** hat ein Timeout für {minuten} Minuten erhalten. Grund: {grund}")
        except discord.Forbidden:
            await ctx.send("❌ Ich habe nicht die erforderlichen Berechtigungen, um diesen Benutzer stummzuschalten.")

async def setup(bot):
    await bot.add_cog(Timeout(bot))
