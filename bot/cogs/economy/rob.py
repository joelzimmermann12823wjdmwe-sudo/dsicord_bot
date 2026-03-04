from discord.ext import commands

class Rob(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="rob")
    async def _rob(self, ctx):
        await ctx.send(f"💰 Economy: rob erfolgreich.")

async def setup(bot): await bot.add_cog(Rob(bot))
