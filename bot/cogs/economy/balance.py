from discord.ext import commands

class Balance(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="balance")
    async def _balance(self, ctx):
        await ctx.send(f"💰 Economy: balance erfolgreich.")

async def setup(bot): await bot.add_cog(Balance(bot))
