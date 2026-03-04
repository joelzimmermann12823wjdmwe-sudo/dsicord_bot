from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="ping")
    async def _ping(self, ctx):
        await ctx.send(f"ℹ️ Utility: ping wird ausgeführt.")

async def setup(bot): await bot.add_cog(Ping(bot))
