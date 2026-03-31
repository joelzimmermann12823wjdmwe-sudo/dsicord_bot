import discord
from discord.ext import commands

class AddRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addrole", description="Gibt einem Nutzer eine Rolle.")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, rolle: discord.Role):
        try:
            await member.add_roles(rolle)
            await ctx.send(f"✅ **{member.display_name}** hat die Rolle **{rolle.name}** erhalten.")
        except discord.Forbidden:
            await ctx.send("❌ Ich habe nicht die Rechte, diese Rolle zu vergeben (Rollen-Hierarchie beachten!).")

async def setup(bot):
    await bot.add_cog(AddRole(bot))
