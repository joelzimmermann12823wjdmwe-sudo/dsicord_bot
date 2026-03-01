import discord
from discord.ext import commands
import os, json, asyncio
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

load_dotenv(ROOT / ".env")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

COGS = [
    "Commands.moderation",
    "Commands.tickets",
    "Commands.logging",
    "Commands.info",
    "Commands.welcome",
    "Commands.automod",
]

def get_guild_ids() -> list[int]:
    raw = os.getenv("GUILD_IDS", "")
    return [int(p.strip()) for p in raw.split(",") if p.strip().isdigit()]

async def sync_commands():
    guild_ids = get_guild_ids()

    # Schritt 1: Globale Commands bei Discord LOESCHEN
    # Das ist der einzige Grund fuer Duplikate:
    # Globale + Guild Commands = Discord zeigt beide
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    print("  [SYNC] Globale Commands geloescht ✅")

    if not guild_ids:
        print("  [SYNC] ⚠️  Keine GUILD_IDS in .env!")
        print("  [SYNC]    Beispiel: GUILD_IDS=123456789012345678")
        return

    # Schritt 2: Fuer jede Guild in .env sofort syncen
    for gid in guild_ids:
        try:
            g = discord.Object(id=gid)
            bot.tree.clear_commands(guild=g)   # alte Guild-Commands loeschen
            await bot.tree.sync(guild=g)       # Loeschung bestaetigen
            bot.tree.copy_global_to(guild=g)   # aktuelle Commands kopieren
            synced = await bot.tree.sync(guild=g)  # syncen
            print(f"  [SYNC] ✅ {len(synced)} Commands auf Guild {gid}")
        except discord.Forbidden:
            print(f"  [SYNC] ❌ Guild {gid}: Keine Berechtigung")
        except discord.NotFound:
            print(f"  [SYNC] ❌ Guild {gid}: Server nicht gefunden")
        except Exception as e:
            print(f"  [SYNC] ❌ Guild {gid}: {e}")

@bot.event
async def on_ready():
    print("====================================")
    print(f"  NEON BOT online!")
    print(f"  Eingeloggt als: {bot.user}")
    print(f"  Server: {len(bot.guilds)}")
    print("====================================")

    with open(DATA / "bot_guilds.json", "w") as f:
        json.dump([str(g.id) for g in bot.guilds], f)

    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{len(bot.guilds)} Server | /help"
    ))

    await sync_commands()
    print("  [SYNC] Fertig — keine Duplikate!")
    print("====================================")

@bot.event
async def on_guild_join(guild):
    try:
        with open(DATA / "bot_guilds.json") as f:
            guilds = json.load(f)
    except:
        guilds = []
    if str(guild.id) not in guilds:
        guilds.append(str(guild.id))
    with open(DATA / "bot_guilds.json", "w") as f:
        json.dump(guilds, f)
    try:
        g = discord.Object(id=guild.id)
        bot.tree.copy_global_to(guild=g)
        synced = await bot.tree.sync(guild=g)
        print(f"  [SYNC] ✅ {len(synced)} Commands auf {guild.name} (neu beigetreten)")
    except Exception as e:
        print(f"  [SYNC] ❌ {guild.name}: {e}")

@bot.event
async def on_guild_remove(guild):
    try:
        with open(DATA / "bot_guilds.json") as f:
            guilds = json.load(f)
        guilds = [g for g in guilds if g != str(guild.id)]
        with open(DATA / "bot_guilds.json", "w") as f:
            json.dump(guilds, f)
    except:
        pass

async def main():
    async with bot:
        print("  Lade Cogs...")
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"  [+] {cog}")
            except Exception as e:
                print(f"  [-] Fehler bei {cog}: {e}")
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
