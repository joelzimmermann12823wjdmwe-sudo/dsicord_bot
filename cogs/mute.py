import discord
from discord.ext import commands
import datetime

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="mute", description="Schaltet einen Nutzer im Textchat stumm (Timeout).")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minuten: int, *, grund: str = "Kein Grund"):
        try:
            dauer = datetime.timedelta(minutes=minuten)
            await member.timeout(dauer, reason=grund)
            await ctx.send(f"✅ **{member.display_name}** wurde für {minuten} Minuten stummgeschaltet.")
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte, um diesen Nutzer stummzuschalten.")

async def setup(bot):
    await bot.add_cog(Mute(bot))
