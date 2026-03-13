import discord
from discord.ext import commands

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unmute", description="Hebt die Stummschaltung (Timeout) eines Nutzers auf.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, grund: str = "Kein Grund"):
        try:
            await member.timeout(None, reason=grund)
            await ctx.send(f"✅ Die Stummschaltung von **{member.display_name}** wurde aufgehoben.")
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte, um die Stummschaltung aufzuheben.")

async def setup(bot):
    await bot.add_cog(Unmute(bot))
