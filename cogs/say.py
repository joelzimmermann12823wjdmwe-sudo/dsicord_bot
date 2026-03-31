from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command(name="say")
    async def say(self, ctx: commands.Context, *, message: str):
        await ctx.message.delete()
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Say(bot))
