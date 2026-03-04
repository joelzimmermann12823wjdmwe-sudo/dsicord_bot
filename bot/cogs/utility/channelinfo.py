from discord.ext import commands

class Channelinfo(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="channelinfo")
    async def _channelinfo(self, ctx):
        await ctx.send(f"ℹ️ Utility: channelinfo wird ausgeführt.")

async def setup(bot): await bot.add_cog(Channelinfo(bot))
