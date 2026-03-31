import discord
from discord.ext import commands

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_nicknames=True)
    @commands.hybrid_command(name="nick", description="Ändert den Nickname eines Nutzers.")
    async def change_nick(self, ctx: commands.Context, member: discord.Member, *, nickname: str):
        await member.edit(nick=nickname)
        await ctx.send(f"✅ Nickname von {member.mention} wurde zu {nickname} geändert.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.hybrid_command(name="resetnick", description="Setzt den Nickname eines Nutzers zurück.")
    async def reset_nick(self, ctx: commands.Context, member: discord.Member):
        await member.edit(nick=None)
        await ctx.send(f"✅ Nickname von {member.mention} wurde zurückgesetzt.")


async def setup(bot):
    await bot.add_cog(Nickname(bot))
