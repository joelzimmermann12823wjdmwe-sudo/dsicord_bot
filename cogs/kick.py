import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="kick", description="Kickt ein Mitglied vom Server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, grund: str):
        embed = discord.Embed(title="👢 Du wurdest gekickt", color=discord.Color.orange())
        embed.add_field(name="Server", value=ctx.guild.name)
        embed.add_field(name="Grund", value=grund)
        
        try:
            await member.send(embed=embed)
        except:
            pass
            
        await member.kick(reason=grund)
        await ctx.send(f"👢 **{member.name}** wurde gekickt. Grund: {grund}")

async def setup(bot):
    await bot.add_cog(Kick(bot))