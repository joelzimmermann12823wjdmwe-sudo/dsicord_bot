import discord
from discord.ext import commands
from bot.utils.config_manager import save_config
class SetWelcome(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        save_config(ctx.guild.id, "welcome", {"enabled": True, "channel": str(channel.id)})
        await ctx.send(f"⚙️ Dashboard synchronisiert: Welcome-Channel ist nun {channel.mention}")
async def setup(bot): await bot.add_cog(SetWelcome(bot))
