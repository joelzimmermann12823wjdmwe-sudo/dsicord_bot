from discord.ext import commands

class Remind(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="remind")
    async def _remind(self, ctx):
        await ctx.send(f"ℹ️ Utility: remind wird ausgeführt.")

async def setup(bot): await bot.add_cog(Remind(bot))
