import discord
from discord.ext import commands
import datetime

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Hilfe-Menü")
    async def help(self, ctx):
        embed = discord.Embed(title="⚡ Neon Bot Hilfe", color=0x00ffff)
        embed.add_field(name="🛡️ Moderation", value="`ban`, `kick`, `mute`, `unmute`, `clear`, `nuke`, `softban`.", inline=False)
        embed.add_field(name="⚙️ Admin", value="`lock`, `unlock`, `addrole`, `removerole`, `nick`, `slowmode`.", inline=False)
        embed.add_field(name="🔗 Kontakt", value="🌐 [Website](https://neon-bot-2026.vercel.app/)\n📧 dev-jojo@proton.me", inline=False)
        embed.set_footer(text="Nutze !help oder /help")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))