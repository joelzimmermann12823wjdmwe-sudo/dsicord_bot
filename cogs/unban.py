import discord
from discord.ext import commands
import datetime

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unban", description="Entbannt einen zuvor gesperrten Nutzer per ID.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str):
        user = await self.bot.fetch_user(int(user_id))
        await ctx.guild.unban(user)
        await ctx.send(f"🔓 {user.name} erfolgreich entbannt.")

async def setup(bot):
    await bot.add_cog(Unban(bot))