import discord
from discord.ext import commands

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unban", description="Entbannt einen Nutzer vom Server.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str, *, grund: str = "Kein Grund angegeben"):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await ctx.guild.unban(user, reason=grund)
            await ctx.send(f"✅ **{user.name}** wurde entbannt. Grund: {grund}")
        except ValueError:
            await ctx.send("❌ Bitte gib eine gültige Benutzer-ID an.")
        except discord.NotFound:
            await ctx.send("❌ Dieser Nutzer wurde nicht in der Bannliste gefunden.")

async def setup(bot):
    await bot.add_cog(Unban(bot))
