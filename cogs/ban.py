import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="Bannt einen Benutzer vom Server.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, grund: str = "Kein Grund angegeben"):
        try:
            await member.ban(reason=grund)
            await ctx.send(f"✅ **{member.display_name}** wurde erfolgreich gebannt. Grund: {grund}")
        except discord.Forbidden:
            await ctx.send("❌ Ich habe nicht die erforderlichen Berechtigungen, um diesen Benutzer zu bannen.")
        except Exception as e:
            await ctx.send(f"❌ Ein Fehler ist aufgetreten: {e}")

async def setup(bot):
    await bot.add_cog(Ban(bot))
