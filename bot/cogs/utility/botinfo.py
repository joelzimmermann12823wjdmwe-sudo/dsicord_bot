from discord.ext import commands

class Botinfo(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="botinfo")
    async def _botinfo(self, ctx):
        await ctx.send(f"ℹ️ Utility: botinfo wird ausgeführt.")

async def setup(bot): await bot.add_cog(Botinfo(bot))
