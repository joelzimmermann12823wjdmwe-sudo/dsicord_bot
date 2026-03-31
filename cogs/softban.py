import discord
from discord.ext import commands

class Softban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="softban", description="Bannt und entbannt sofort, um Nachrichten zu löschen.")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, grund: str = "Softban"):
        try:
            await member.ban(reason=grund, delete_message_days=7)
            await ctx.guild.unban(member, reason="Softban Entbannung")
            await ctx.send(f"✅ **{member.display_name}** wurde ge-softbannt (Nachrichten gelöscht).")
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte für diese Aktion.")

async def setup(bot):
    await bot.add_cog(Softban(bot))
