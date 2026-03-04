from discord.ext import commands

class Shop(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="shop")
    async def _shop(self, ctx):
        await ctx.send(f"💰 Economy: shop erfolgreich.")

async def setup(bot): await bot.add_cog(Shop(bot))
