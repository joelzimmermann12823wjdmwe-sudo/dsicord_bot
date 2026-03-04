from discord.ext import commands

class Pay(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="pay")
    async def _pay(self, ctx):
        await ctx.send(f"💰 Economy: pay erfolgreich.")

async def setup(bot): await bot.add_cog(Pay(bot))
