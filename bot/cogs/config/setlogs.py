from discord.ext import commands
from bot.utils.config_manager import save_config

class Setlogs(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @commands.command(name="setlogs")
    async def _setlogs(self, ctx, value: str):
        save_config(ctx.guild.id, "setlogs", {"value": value})
        await ctx.send(f"⚙️ {cmd} auf '{value}' gesetzt und im Dashboard aktualisiert.")

async def setup(bot): await bot.add_cog(Setlogs(bot))
