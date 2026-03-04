from discord.ext import commands

class Uptime(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="uptime")
    async def _uptime(self, ctx):
        await ctx.send(f"ℹ️ Utility: uptime wird ausgeführt.")

async def setup(bot): await bot.add_cog(Uptime(bot))
