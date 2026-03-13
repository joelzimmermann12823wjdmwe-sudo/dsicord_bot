import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hilfe", description="Zeigt die System-Dokumentation von Neon Bot an.")
    async def hilfe(self, ctx):
        embed = discord.Embed(title="Neon Bot | System-Dokumentation", description="Hier findest du eine vollständige Liste aller integrierten Module und Befehle.", color=discord.Color.teal())
        
        embed.add_field(name="🛡️ Moderation", value="`/ban`, `/unban`, `/softban`, `/kick`, `/mute`, `/unmute`, `/clear`, `/slowmode`, `/nick`", inline=False)
        embed.add_field(name="⚙️ Administration & Schutz", value="`/automod`, `/link_filter`, `/lock`, `/unlock`, `/whitelist`, `/settings`, `/logging`, `/welcome`", inline=False)
        embed.add_field(name="🎭 Rollen & Sprachkanäle", value="`/addrole`, `/removerole`, `/vckick`, `/vcmute`, `/vcunmute`", inline=False)
        embed.add_field(name="📊 Info & Statistik", value="`/hilfe`, `/userinfo`, `/serverinfo`, `/avatar`, `/ping`", inline=False)
        embed.add_field(name="💻 System-Module", value="`/owner`, `/status_bot`, `/test_cmd`", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    # Wichtig: main.py muss bot.remove_command("help") ausführen, wenn der Befehl "help" heißen soll. 
    # Hier nennen wir ihn der Einfachheit halber "hilfe".
    await bot.add_cog(Help(bot))
