from discord.ext import commands

class Work(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="work")
    async def _work(self, ctx):
        await ctx.send(f"💰 Economy: work erfolgreich.")

async def setup(bot): await bot.add_cog(Work(bot))
