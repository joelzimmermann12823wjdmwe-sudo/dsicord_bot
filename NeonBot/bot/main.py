import discord
from discord.ext import commands
import os, json, asyncio
from dotenv import load_dotenv
from pathlib import Path
from aiohttp import web

ROOT = Path(__file__).resolve().parent.parent
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

# ── Minimaler Web-Server fuer Render ────────────────────────
# Render braucht einen offenen Port sonst stoppt es den Service
# Dieser Server macht nichts ausser "OK" zurueckzugeben
async def start_webserver():
    async def handle(request):
        return web.Response(text="⚡ Neon Bot is online!")

    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/health", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))  # Render setzt PORT automatisch
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"  [WEB] Server laeuft auf Port {port} ✅")

# ── Sync ─────────────────────────────────────────────────────
async def sync_commands() -> None:
    print("  [SYNC] Starte Global-Sync...")
    try:
        synced = await bot.tree.sync()
        print(f"  [SYNC] ✅ {len(synced)} Commands global registriert")
    except Exception as e:
        print(f"  [SYNC] ❌ {e}")

# ── Bot Events ───────────────────────────────────────────────
@bot.event
async def on_ready():
    print("====================================")
    print(f"  ⚡ NEON BOT online!")
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
    print("====================================")

@bot.event
async def on_guild_join(guild: discord.Guild):
    try:
        with open(DATA / "bot_guilds.json") as f:
            guilds = json.load(f)
    except:
        guilds = []
    if str(guild.id) not in guilds:
        guilds.append(str(guild.id))
    with open(DATA / "bot_guilds.json", "w") as f:
        json.dump(guilds, f)
    print(f"  [BOT] Neuer Server: {guild.name} ({guild.id})")

@bot.event
async def on_guild_remove(guild: discord.Guild):
    try:
        with open(DATA / "bot_guilds.json") as f:
            guilds = json.load(f)
        guilds = [g for g in guilds if g != str(guild.id)]
        with open(DATA / "bot_guilds.json", "w") as f:
            json.dump(guilds, f)
    except:
        pass

# ── Main ─────────────────────────────────────────────────────
async def main():
    # Web-Server und Bot gleichzeitig starten
    await start_webserver()

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
