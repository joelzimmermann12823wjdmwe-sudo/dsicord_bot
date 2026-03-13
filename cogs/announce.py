import discord
from discord.ext import commands
from typing import Optional

class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="ankündigung", 
        description="Sendet eine formatierte Nachricht in einen Kanal."
    )
    @commands.has_permissions(administrator=True)
    async def announce(
        self, 
        ctx, 
        kanal: discord.TextChannel, 
        nachricht: str, 
        titel: str = "Ankündigung", 
        bild_url: Optional[str] = None
    ):
        """
        Erstellt eine Ankündigung. 
        Links in der Nachricht werden von Discord automatisch erkannt.
        """
        embed = discord.Embed(
            title=titel,
            description=nachricht.replace("\\n", "\n"), # Erlaubt Zeilenumbrüche mit \n
            color=discord.Color.gold()
        )
        
        embed.set_footer(text=f"Gesendet von {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        if bild_url:
            # Einfache Validierung, ob es wie ein Link aussieht
            if bild_url.startswith("http"):
                embed.set_image(url=bild_url)
        
        try:
            await kanal.send(embed=embed)
            await ctx.send(f"✅ Ankündigung wurde erfolgreich in {kanal.mention} gesendet!", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ Ich habe keine Rechte, in diesen Kanal zu schreiben.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Announce(bot))
