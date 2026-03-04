from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="poll")
    async def _poll(self, ctx):
        await ctx.send(f"ℹ️ Utility: poll wird ausgeführt.")

async def setup(bot): await bot.add_cog(Poll(bot))
