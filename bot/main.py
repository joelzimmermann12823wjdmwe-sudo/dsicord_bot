import discord
import os
import json
from discord.ext import commands
from dotenv import load_dotenv
from bot.utils.config_manager import load_config

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")

@bot.event
async def on_member_join(member):
    cfg = load_config(member.guild.id)
    
    # 1. Auto-Rolle
    ar_cfg = cfg.get("auto_role", {})
    if ar_cfg.get("role"):
        role = member.guild.get_role(int(ar_cfg["role"]))
        if role: await member.add_roles(role)
    
    # 2. Welcome Message
    w_cfg = cfg.get("welcome", {})
    if w_cfg.get("enabled") and w_cfg.get("channel"):
        channel = bot.get_channel(int(w_cfg["channel"]))
        if channel:
            msg = w_cfg.get("message", "Willkommen {user}!").replace("{user}", member.mention).replace("{server}", member.guild.name)
            await channel.send(msg)

@bot.event
async def on_message(message):
    if message.author.bot: return
    cfg = load_config(message.guild.id)
    am = cfg.get("automod", {})
    
    # Automod: Badwords Filter
    if am.get("filter_badwords"):
        words = am.get("extra_badwords", [])
        if any(w.lower() in message.content.lower() for w in words):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, achte auf deine Wortwahl!", delete_after=3)
            return

    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))
