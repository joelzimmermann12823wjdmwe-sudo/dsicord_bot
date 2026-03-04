from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="roles")
    async def _roles(self, ctx):
        await ctx.send(f"ℹ️ Utility: roles wird ausgeführt.")

async def setup(bot): await bot.add_cog(Roles(bot))
