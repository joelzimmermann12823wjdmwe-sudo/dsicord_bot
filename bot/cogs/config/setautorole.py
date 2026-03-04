from discord.ext import commands
from bot.utils.config_manager import save_config

class Setautorole(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="setautorole")
    async def _setautorole(self, ctx, value: str):
        save_config(ctx.guild.id, "setautorole", {"value": value})
        await ctx.send(f"⚙️ {cmd} auf '{value}' gesetzt und im Dashboard aktualisiert.")

async def setup(bot): await bot.add_cog(Setautorole(bot))
