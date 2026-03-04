from discord.ext import commands

class Slots(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="slots")
    async def _slots(self, ctx):
        await ctx.send(f"💰 Economy: slots erfolgreich.")

async def setup(bot): await bot.add_cog(Slots(bot))
