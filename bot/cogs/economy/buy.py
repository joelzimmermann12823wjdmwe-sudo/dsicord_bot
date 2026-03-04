from discord.ext import commands

class Buy(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="buy")
    async def _buy(self, ctx):
        await ctx.send(f"💰 Economy: buy erfolgreich.")

async def setup(bot): await bot.add_cog(Buy(bot))
