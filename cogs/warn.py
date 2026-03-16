import discord
from discord.ext import commands
import datetime

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="warn", description="Verwarnt ein Mitglied und sendet eine DM.")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, grund: str):
        # 1. Datenbank-Eintrag (nutzt self.bot.db aus deiner main.py)
        if hasattr(self.bot, 'db') and self.bot.db:
            try:
                self.bot.db.table("warns").insert({
                    "user_id": str(member.id),
                    "guild_id": str(ctx.guild.id),
                    "reason": grund,
                    "moderator_id": str(ctx.author.id)
                }).execute()
            except Exception as e:
                print(f"DB-Fehler: {e}")

        # 2. DM an User
        embed = discord.Embed(title="⚠️ Verwarnung erhalten", color=discord.Color.gold(), timestamp=datetime.datetime.now())
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.add_field(name="Grund", value=grund, inline=True)
        embed.add_field(name="Link zum Server", value=f"https://discord.com/channels/{ctx.guild.id}", inline=False)
        
        dm_sent = True
        try:
            await member.send(embed=embed)
        except:
            dm_sent = False

        await ctx.send(f"✅ **{member.name}** wurde verwarnt. {'(DM gesendet)' if dm_sent else '(DM fehlgeschlagen)'}")

async def setup(bot):
    await bot.add_cog(Warn(bot))