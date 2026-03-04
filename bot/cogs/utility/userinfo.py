from discord.ext import commands

class Userinfo(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="userinfo")
    async def _userinfo(self, ctx):
        await ctx.send(f"ℹ️ Utility: userinfo wird ausgeführt.")

async def setup(bot): await bot.add_cog(Userinfo(bot))
