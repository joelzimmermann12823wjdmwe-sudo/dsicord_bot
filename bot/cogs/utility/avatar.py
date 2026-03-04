from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="avatar")
    async def _avatar(self, ctx):
        await ctx.send(f"ℹ️ Utility: avatar wird ausgeführt.")

async def setup(bot): await bot.add_cog(Avatar(bot))
