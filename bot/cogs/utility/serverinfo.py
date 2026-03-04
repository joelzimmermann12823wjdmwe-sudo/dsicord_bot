from discord.ext import commands

class Serverinfo(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="serverinfo")
    async def _serverinfo(self, ctx):
        await ctx.send(f"ℹ️ Utility: serverinfo wird ausgeführt.")

async def setup(bot): await bot.add_cog(Serverinfo(bot))
