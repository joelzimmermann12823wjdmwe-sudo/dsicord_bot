import sys

import discord
from discord.ext import commands


class StatusBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="status_bot",
        description="Zeigt den aktuellen System-Status an und sendet einen Statusbericht.",
    )
    async def status_bot(self, ctx):
        embed = discord.Embed(title="System-Status", color=discord.Color.green())
        embed.add_field(name="Serveranzahl", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Nutzeranzahl", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Python Version", value=sys.version.split()[0], inline=True)
        embed.add_field(name="discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Latenz", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

        reporter = getattr(self.bot, "send_status_report", None)
        if reporter is not None:
            await reporter(
                "Manueller Statusbericht",
                "Der Statusbericht wurde manuell ueber /status_bot angefordert.",
                color=discord.Color.blue(),
                details={
                    "Server": f"{ctx.guild} ({ctx.guild.id})" if ctx.guild else "DM",
                    "Kanal": getattr(ctx.channel, "mention", "unbekannt"),
                    "User": f"{ctx.author} ({ctx.author.id})",
                    "Latenz": f"{round(self.bot.latency * 1000)}ms",
                    "Serveranzahl": len(self.bot.guilds),
                },
                ping_role=True,
            )


async def setup(bot):
    await bot.add_cog(StatusBot(bot))
