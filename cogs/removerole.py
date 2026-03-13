import discord
from discord.ext import commands

class RemoveRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="removerole", description="Entfernt eine Rolle von einem Nutzer.")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, rolle: discord.Role):
        try:
            await member.remove_roles(rolle)
            await ctx.send(f"✅ Die Rolle **{rolle.name}** wurde von **{member.display_name}** entfernt.")
        except discord.Forbidden:
            await ctx.send("❌ Ich habe nicht die Rechte, diese Rolle zu entfernen.")

async def setup(bot):
    await bot.add_cog(RemoveRole(bot))
