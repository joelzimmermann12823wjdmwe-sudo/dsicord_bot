import discord
from discord.ext import commands
import os

class NeonBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), help_command=None)

    async def setup_hook(self):
        for filename in os.listdir('./bot/Commands'):
            if filename.endswith('.py') and filename != 'helper.py':
                await self.load_extension(f'bot.Commands.{filename[:-3]}')

bot = NeonBot()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    fmt = await bot.tree.sync()
    await ctx.send(f"✅ {len(fmt)} Slash-Commands synchronisiert!")

bot.run(os.getenv('TOKEN'))
