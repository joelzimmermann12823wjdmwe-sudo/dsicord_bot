import discord
from discord.ext import commands
import datetime

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="timeout", description="Versetzt ein Mitglied in den Timeout (Stummschaltung).")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minuten: int, *, grund: str):
        duration = datetime.timedelta(minutes=minuten)
        
        embed = discord.Embed(title="⏳ Timeout erhalten", color=discord.Color.blue())
        embed.add_field(name="Server", value=ctx.guild.name)
        embed.add_field(name="Dauer", value=f"{minuten} Minuten")
        embed.add_field(name="Grund", value=grund)
        embed.add_field(name="Link zum Server", value=f"https://discord.com/channels/{ctx.guild.id}")
        
        try:
            await member.send(embed=embed)
        except:
            pass
            
        await member.timeout(duration, reason=grund)
        await ctx.send(f"⏳ **{member.name}** wurde für {minuten} Minuten stummgeschaltet.")

async def setup(bot):
    await bot.add_cog(Timeout(bot))