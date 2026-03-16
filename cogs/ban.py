import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="Bannt ein Mitglied und informiert es per DM.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, grund: str):
        # DM vor dem Bann senden
        embed = discord.Embed(title="🔨 Du wurdest gebannt", color=discord.Color.red())
        embed.add_field(name="Server", value=ctx.guild.name)
        embed.add_field(name="Grund", value=grund)
        embed.set_footer(text="Aktion: Permanent")
        
        try:
            await member.send(embed=embed)
        except:
            pass
        
        await member.ban(reason=grund)
        await ctx.send(f"🔨 **{member.name}** wurde permanent gebannt. Grund: {grund}")

async def setup(bot):
    await bot.add_cog(Ban(bot))