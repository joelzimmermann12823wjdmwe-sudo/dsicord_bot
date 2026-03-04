from discord.ext import commands

class Membercount(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="membercount")
    async def _membercount(self, ctx):
        await ctx.send(f"ℹ️ Utility: membercount wird ausgeführt.")

async def setup(bot): await bot.add_cog(Membercount(bot))
