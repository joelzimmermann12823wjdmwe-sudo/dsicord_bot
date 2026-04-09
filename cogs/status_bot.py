from __future__ import annotations

import asyncio
import json
import os
from urllib.request import urlopen

import discord
from discord.ext import commands


def get_local_status_url() -> str:
    port = (os.getenv("PORT") or "8000").strip()
    return f"http://127.0.0.1:{port}/status.json"


def fetch_status_snapshot(url: str) -> dict:
    with urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def format_uptime(seconds: int | None) -> str:
    if seconds is None:
        return "-"

    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)

    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


class StatusBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _load_snapshot(self) -> dict:
        target_url = get_local_status_url()
        try:
            return await asyncio.to_thread(fetch_status_snapshot, target_url)
        except Exception:
            builder = getattr(self.bot, "build_status_snapshot", None)
            if callable(builder):
                return builder()
            raise

    @commands.hybrid_command(
        name="status_bot",
        description="Zeigt den aktuellen Status aus der internen Status-Website an.",
    )
    async def status_bot(self, ctx):
        snapshot = await self._load_snapshot()

        status = str(snapshot.get("status", "unknown")).lower()
        color_map = {
            "ok": discord.Color.green(),
            "degraded": discord.Color.orange(),
            "error": discord.Color.red(),
        }

        embed = discord.Embed(
            title="System-Status",
            description=f"Live-Daten von `{get_local_status_url()}`",
            color=color_map.get(status, discord.Color.blurple()),
        )
        embed.add_field(name="Status", value=status.upper(), inline=True)
        embed.add_field(name="Ready", value=str(snapshot.get("ready")), inline=True)
        embed.add_field(name="Latency", value=f"{snapshot.get('latency_ms', '-')}" + "ms", inline=True)
        embed.add_field(name="Guilds", value=str(snapshot.get("guild_count", 0)), inline=True)
        embed.add_field(name="RAM", value=f"{snapshot.get('memory_rss_mb', '-')}" + " MB", inline=True)
        embed.add_field(name="Uptime", value=format_uptime(snapshot.get("uptime_seconds")), inline=True)

        runtime = snapshot.get("runtime", {})
        embed.add_field(name="Login State", value=str(runtime.get("login_state", "-")), inline=True)
        embed.add_field(
            name="Commands",
            value=(
                f"{runtime.get('commands_completed', 0)} ok / "
                f"{runtime.get('commands_failed', 0)} fail"
            ),
            inline=True,
        )

        queues = snapshot.get("queues", {})
        command_queue = queues.get("commands", {})
        api_queue = queues.get("api", {})
        embed.add_field(
            name="Queues",
            value=(
                f"Cmd {command_queue.get('running', 0)}/{command_queue.get('limit', 0)} "
                f"(wait {command_queue.get('waiting', 0)})\n"
                f"API {api_queue.get('running', 0)}/{api_queue.get('limit', 0)} "
                f"(wait {api_queue.get('waiting', 0)})"
            ),
            inline=False,
        )

        database = snapshot.get("database", {})
        embed.add_field(
            name="Datenbank",
            value="verbunden" if database.get("ok") else truncate(str(database.get("error", "fehlerhaft")), 300),
            inline=False,
        )

        issues = snapshot.get("issues", [])
        if issues:
            lines = []
            for issue in issues[:3]:
                summary = truncate(str(issue.get("summary", "-")), 160)
                source = issue.get("source", "-")
                count = issue.get("count", 1)
                lines.append(f"[{issue.get('severity', '-').upper()}] {source}: {summary} x{count}")
            embed.add_field(name="Letzte Fehler", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="Letzte Fehler", value="Keine aktuellen Fehler gespeichert.", inline=False)

        routes = snapshot.get("routes", {})
        if routes.get("status_page"):
            embed.add_field(name="Status-Seite", value=routes["status_page"], inline=False)

        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


async def setup(bot):
    await bot.add_cog(StatusBot(bot))
