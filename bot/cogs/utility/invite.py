from discord.ext import commands

class Invite(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="invite")
    async def _invite(self, ctx):
        await ctx.send(f"ℹ️ Utility: invite wird ausgeführt.")

async def setup(bot): await bot.add_cog(Invite(bot))
