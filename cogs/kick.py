import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="kick", description="Wirft einen Benutzer vom Server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, grund: str = "Kein Grund angegeben"):
        try:
            await member.kick(reason=grund)
            await ctx.send(f"✅ **{member.display_name}** wurde erfolgreich gekickt. Grund: {grund}")
        except discord.Forbidden:
            await ctx.send("❌ Ich habe nicht die erforderlichen Berechtigungen, um diesen Benutzer zu kicken.")

async def setup(bot):
    await bot.add_cog(Kick(bot))
