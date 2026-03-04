from discord.ext import commands
from bot.utils.config_manager import save_config

class Setwelcome(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="setwelcome")
    async def _setwelcome(self, ctx, value: str):
        save_config(ctx.guild.id, "setwelcome", {"value": value})
        await ctx.send(f"⚙️ {cmd} auf '{value}' gesetzt und im Dashboard aktualisiert.")

async def setup(bot): await bot.add_cog(Setwelcome(bot))
