import discord
from discord.ext import commands
import datetime

class Softban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="softban", description="Bannt und entbannt sofort (löscht die Nachrichten des Nutzers).")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member):
        await member.ban(reason="Softban")
        await member.unban()
        await ctx.send(f"🍦 Softban für {member.name} erfolgreich.")

async def setup(bot):
    await bot.add_cog(Softban(bot))