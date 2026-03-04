from discord.ext import commands

class Translate(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="translate")
    async def _translate(self, ctx):
        await ctx.send(f"ℹ️ Utility: translate wird ausgeführt.")

async def setup(bot): await bot.add_cog(Translate(bot))
