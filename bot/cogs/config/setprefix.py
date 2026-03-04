from discord.ext import commands
from bot.utils.config_manager import save_config

class Setprefix(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="setprefix")
    async def _setprefix(self, ctx, value: str):
        save_config(ctx.guild.id, "setprefix", {"value": value})
        await ctx.send(f"⚙️ {cmd} auf '{value}' gesetzt und im Dashboard aktualisiert.")

async def setup(bot): await bot.add_cog(Setprefix(bot))
