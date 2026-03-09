import discord
from discord.ext import commands
import os, sys, asyncio, logging
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
@app.route('/')
def home(): return "Neon Bot Online"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

load_dotenv()
class NeonBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), help_command=None)

    async def setup_hook(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root not in sys.path: sys.path.insert(0, root)
        cogs_path = os.path.join(root, "cogs")
        for file in os.listdir(cogs_path):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
        await self.tree.sync()

    async def on_ready(self):
        print(f"🚀 {self.user} online auf {len(self.guilds)} Servern!")
        await self.change_presence(activity=discord.Game(name="/help"))

async def start():
    Thread(target=run_flask, daemon=True).start()
    bot = NeonBot()
    async with bot: await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__": asyncio.run(start())
