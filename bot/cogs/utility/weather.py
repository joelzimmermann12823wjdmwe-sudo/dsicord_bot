from discord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="weather")
    async def _weather(self, ctx):
        await ctx.send(f"ℹ️ Utility: weather wird ausgeführt.")

async def setup(bot): await bot.add_cog(Weather(bot))
