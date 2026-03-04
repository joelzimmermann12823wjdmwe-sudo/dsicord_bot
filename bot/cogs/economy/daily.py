from discord.ext import commands

class Daily(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="daily")
    async def _daily(self, ctx):
        await ctx.send(f"💰 Economy: daily erfolgreich.")

async def setup(bot): await bot.add_cog(Daily(bot))
