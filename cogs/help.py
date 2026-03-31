from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Listet alle verfügbaren Befehle auf.")
    async def help_command(self, ctx: commands.Context):
        commands_list = [
            "ban, kick, mute, unmute, timeout, warn, clear, lock, unlock, slowmode",
            "addrole, removerole, nick, resetnick",
            "ping, serverinfo, userinfo, avatar, invite, poll, say",
        ]
        await ctx.send("📘 Verfügbare Befehle:\n" + "\n".join(commands_list))


def setup(bot):
    bot.add_cog(Help(bot))
