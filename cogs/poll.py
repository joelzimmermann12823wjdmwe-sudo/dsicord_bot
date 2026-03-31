from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="poll")
    async def poll(self, ctx: commands.Context, *, question: str):
        message = await ctx.send(f"📊 Umfrage: {question}")
        await message.add_reaction("👍")
        await message.add_reaction("👎")


def setup(bot):
    bot.add_cog(Poll(bot))
