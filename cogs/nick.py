import discord
from discord.ext import commands

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nick", description="Ändert den Nicknamen eines Nutzers.")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, neuer_name: str = None):
        try:
            await member.edit(nick=neuer_name)
            if neuer_name:
                await ctx.send(f"✅ Der Nickname wurde zu **{neuer_name}** geändert.")
            else:
                await ctx.send(f"✅ Der Nickname von **{member.name}** wurde zurückgesetzt.")
        except discord.Forbidden:
            await ctx.send("❌ Mir fehlen die Rechte oder meine Rolle ist nicht hoch genug.")

async def setup(bot):
    await bot.add_cog(Nick(bot))
