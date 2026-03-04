import discord
from discord.ext import commands
from bot.utils.config_manager import load_config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason="Kein Grund"):
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member} wurde gekickt. Grund: {reason}")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason="Kein Grund"):
        await member.ban(reason=reason)
        await ctx.send(f"🚫 {member} wurde gebannt.")

    @commands.command()
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(f"🧹 {amount} Nachrichten gelöscht.", delete_after=3)

    # ... hier folgen intern: unban, softban, tempban, warn, warnings, clearwarns, 
    # slowmode, lock, unlock, timeout, untimeout, nick, vckick, vcmute
