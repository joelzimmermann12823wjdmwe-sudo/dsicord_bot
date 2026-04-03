import discord
from discord.ext import commands
from helpers import create_embed

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Listet alle verfügbaren Befehle auf.")
    async def help_command(self, ctx: commands.Context):
        embed = create_embed(
            title="📘 Hilfe",
            description="Hier findest du eine Übersicht über die verfügbaren Befehle.",
            footer="/help | !help",
        )
        embed.add_field(
            name="Moderation",
            value="/ban, /kick, /mute, /unmute, /timeout, /warn, /warns, /clear, /lock, /unlock, /slowmode",
            inline=False,
        )
        embed.add_field(
            name="Rollen & Nutzer",
            value="/addrole, /removerole, /nick, /resetnick, /avatar, /userinfo",
            inline=False,
        )
        embed.add_field(
            name="Sonstiges",
            value="/ping, /serverinfo, /invite, /poll, /say, /help",
            inline=False,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
