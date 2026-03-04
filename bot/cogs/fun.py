import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball")
    async def eightball(self, ctx, *, question):
        responses = ["Ja", "Nein", "Vielleicht", "Frag später nochmal"]
        await ctx.send(f"🎱 {random.choice(responses)}")

    @commands.command()
    async def meme(self, ctx):
        # Hier könnte eine API-Abfrage für Memes stehen
        await ctx.send("🖼️ Hier wäre ein lustiges Meme!")

    # ... weitere: dice, flip, hug, slap, kill, ship, joke, hack, 
    # work, balance, daily, slots, rob, shop, leaderboard
