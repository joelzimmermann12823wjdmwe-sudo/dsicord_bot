from __future__ import annotations

import asyncio
import gc
import html
import json
import sys
import threading
import time
import traceback
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Awaitable, Callable
from urllib.parse import urlsplit

import discord


RECENT_ISSUE_LIMIT = 100
RECENT_ISSUES_ON_PAGE = 15


def utcnow() -> datetime:
    return discord.utils.utcnow()


def isoformat(timestamp: datetime | None) -> str | None:
    if timestamp is None:
        return None
    return timestamp.isoformat().replace("+00:00", "Z")


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return isoformat(value)
    if isinstance(value, BaseException):
        return f"{type(value).__name__}: {value}"
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, deque)):
        return [_json_safe(item) for item in value]
    return value


def log_event(level: str, event: str, **fields: Any) -> None:
    payload = {
        "ts": isoformat(utcnow()),
        "level": level,
        "event": event,
        **{key: _json_safe(value) for key, value in fields.items()},
    }
    stream = sys.stderr if level in {"warning", "error", "critical"} else sys.stdout
    print(json.dumps(payload, ensure_ascii=True, separators=(",", ":")), file=stream, flush=True)


def truncate_text(value: Any, limit: int = 1200) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def human_duration(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def get_process_memory_mb() -> float | None:
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as proc_status:
            for line in proc_status:
                if line.startswith("VmRSS:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return round(int(parts[1]) / 1024, 2)
    except OSError:
        pass

    try:
        import resource  # type: ignore

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform == "darwin":
            return round(usage / (1024 * 1024), 2)
        return round(usage / 1024, 2)
    except Exception:
        return None


class ExecutionGate:
    def __init__(self, limit: int):
        self.limit = max(1, int(limit))
        self._semaphore = asyncio.Semaphore(self.limit)
        self._lock = threading.Lock()
        self.waiting = 0
        self.running = 0

    @asynccontextmanager
    async def slot(self):
        with self._lock:
            self.waiting += 1
        acquired = False
        try:
            await self._semaphore.acquire()
            acquired = True
        finally:
            with self._lock:
                self.waiting -= 1
                if acquired:
                    self.running += 1
        try:
            yield
        finally:
            if acquired:
                with self._lock:
                    self.running -= 1
                self._semaphore.release()

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            running = self.running
            waiting = self.waiting
        return {
            "limit": self.limit,
            "running": running,
            "waiting": waiting,
            "available": max(self.limit - running, 0),
        }


class DiscordApiLimiter:
    def __init__(
        self,
        gate: ExecutionGate,
        monitor: RuntimeMonitor,
        *,
        min_interval: float = 0.35,
    ):
        self.gate = gate
        self.monitor = monitor
        self.min_interval = max(0.0, float(min_interval))
        self._interval_lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def _respect_min_interval(self) -> None:
        async with self._interval_lock:
            now = time.monotonic()
            wait_time = self.min_interval - (now - self._last_request_at)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._last_request_at = time.monotonic()

    @staticmethod
    def _retry_after(error: discord.HTTPException, attempt: int) -> float:
        headers = getattr(error.response, "headers", {}) or {}
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                return max(0.5, float(retry_after))
            except (TypeError, ValueError):
                pass

        backoff = (1.0, 2.0, 5.0, 10.0)
        return backoff[min(attempt, len(backoff) - 1)]

    async def run(
        self,
        label: str,
        factory: Callable[[], Awaitable[Any]],
        *,
        retries: int = 3,
    ) -> Any:
        async with self.gate.slot():
            attempt = 0
            while True:
                await self._respect_min_interval()
                try:
                    return await factory()
                except discord.HTTPException as exc:
                    retriable = exc.status == 429 or 500 <= exc.status < 600
                    if not retriable or attempt >= retries:
                        raise

                    delay = self._retry_after(exc, attempt)
                    self.monitor.record_issue(
                        "discord_api",
                        f"API-Aufruf wird erneut versucht: {label}",
                        severity="warning",
                        details={"status": exc.status, "retry_after_seconds": delay},
                    )
                    await asyncio.sleep(delay)
                    attempt += 1


class RuntimeMonitor:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.started_at = utcnow()
        self._lock = threading.Lock()
        self._issues: deque[dict[str, Any]] = deque(maxlen=RECENT_ISSUE_LIMIT)
        self.health_server_port: int | None = None
        self.health_server_started = False
        self.last_ready_at: datetime | None = None
        self.last_disconnect_at: datetime | None = None
        self.last_connect_attempt_at: datetime | None = None
        self.last_connect_error: str | None = None
        self.last_connect_error_at: datetime | None = None
        self.last_restart_at: datetime | None = None
        self.login_state = "starting"
        self.commands_started = 0
        self.commands_completed = 0
        self.commands_failed = 0
        self.events_failed = 0
        self.storage_health: dict[str, Any] = {
            "configured": False,
            "ok": False,
            "error": "Noch nicht geprueft",
        }
        self.storage_checked_at: datetime | None = None

    def mark_health_server(self, port: int) -> None:
        with self._lock:
            self.health_server_port = port
            self.health_server_started = True

    def mark_connect_attempt(self) -> None:
        with self._lock:
            self.last_connect_attempt_at = utcnow()
            self.login_state = "connecting"

    def set_login_state(self, state: str) -> None:
        with self._lock:
            self.login_state = state

    def mark_ready(self) -> None:
        with self._lock:
            self.last_ready_at = utcnow()
            self.last_connect_error = None
            self.last_connect_error_at = None
            self.login_state = "ready"

    def mark_disconnect(self) -> None:
        with self._lock:
            self.last_disconnect_at = utcnow()
            if self.login_state != "config_error":
                self.login_state = "disconnected"

    def mark_restart(self) -> None:
        with self._lock:
            self.last_restart_at = utcnow()
            if self.login_state != "config_error":
                self.login_state = "retrying"

    def mark_sync_completed(self) -> None:
        with self._lock:
            pass

    def update_storage_health(self, health: dict[str, Any]) -> None:
        with self._lock:
            self.storage_health = _json_safe(health)
            self.storage_checked_at = utcnow()

    def record_command_started(self) -> None:
        with self._lock:
            self.commands_started += 1

    def record_command_completed(self) -> None:
        with self._lock:
            self.commands_completed += 1

    def record_command_failed(self) -> None:
        with self._lock:
            self.commands_failed += 1

    def record_event_failed(self) -> None:
        with self._lock:
            self.events_failed += 1

    def record_issue(
        self,
        source: str,
        summary: str,
        *,
        severity: str = "error",
        details: Any | None = None,
        exc: BaseException | None = None,
        emit_console: bool = False,
    ) -> None:
        now = utcnow()
        detail_payload: Any = details
        if exc is not None:
            detail_payload = truncate_text(
                "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
                4000,
            )
        elif detail_payload is not None:
            detail_payload = truncate_text(json.dumps(_json_safe(detail_payload), ensure_ascii=True), 4000)

        issue = {
            "timestamp": isoformat(now),
            "source": source,
            "severity": severity,
            "summary": truncate_text(summary, 600),
            "details": detail_payload,
            "count": 1,
        }

        with self._lock:
            if self._issues:
                latest = self._issues[0]
                same_issue = (
                    latest.get("source") == issue["source"]
                    and latest.get("severity") == issue["severity"]
                    and latest.get("summary") == issue["summary"]
                )
                if same_issue:
                    latest["timestamp"] = issue["timestamp"]
                    latest["count"] = int(latest.get("count", 1)) + 1
                    latest["details"] = issue["details"] or latest.get("details")
                else:
                    self._issues.appendleft(issue)
            else:
                self._issues.appendleft(issue)

            if severity in {"critical", "error"} and "Bot konnte nicht online gehen" in summary:
                self.last_connect_error = issue["summary"]
                self.last_connect_error_at = now

        if emit_console or severity in {"critical"}:
            log_event(
                severity,
                "runtime_issue",
                source=source,
                summary=summary,
                details=detail_payload,
            )

    def build_snapshot(
        self,
        *,
        bot: discord.Client,
        allowed_guild_id: int | None,
        commands_synced: bool,
        token_configured: bool,
        command_gate: ExecutionGate,
        api_gate: ExecutionGate,
        public_base_url: str | None,
    ) -> dict[str, Any]:
        now = utcnow()
        uptime_seconds = int((now - self.started_at).total_seconds())
        latency_ms = round(bot.latency * 1000) if getattr(bot, "user", None) else None
        guild_count = len(getattr(bot, "guilds", []))
        cached_users = len(getattr(bot, "users", []))
        allowed_guild_connected = (
            True
            if allowed_guild_id is None
            else any(guild.id == allowed_guild_id for guild in getattr(bot, "guilds", []))
        )
        storage_health = self.storage_health
        checks = {
            "health_server_online": self.health_server_started,
            "discord_user_available": getattr(bot, "user", None) is not None,
            "discord_ready": bot.is_ready(),
            "commands_synced": commands_synced,
            "token_configured": token_configured,
            "allowed_guild_connected": allowed_guild_connected,
            "storage_initialized": getattr(bot, "storage", None) is not None,
            "database_connected": bool(storage_health.get("ok")),
        }

        ready = (
            checks["discord_ready"]
            and checks["storage_initialized"]
            and checks["database_connected"]
            and checks["token_configured"]
            and checks["allowed_guild_connected"]
        )

        status = "error"
        if ready:
            status = "ok"
        elif checks["health_server_online"] or checks["token_configured"]:
            status = "degraded"

        if latency_ms is not None and latency_ms >= 1200 and status == "ok":
            status = "degraded"

        with self._lock:
            recent_issues = list(self._issues)[:RECENT_ISSUES_ON_PAGE]
            summary = {
                "health_server_port": self.health_server_port,
                "last_ready_at": isoformat(self.last_ready_at),
                "last_disconnect_at": isoformat(self.last_disconnect_at),
                "last_connect_attempt_at": isoformat(self.last_connect_attempt_at),
                "last_connect_error": self.last_connect_error,
                "last_connect_error_at": isoformat(self.last_connect_error_at),
                "last_restart_at": isoformat(self.last_restart_at),
                "login_state": self.login_state,
                "commands_started": self.commands_started,
                "commands_completed": self.commands_completed,
                "commands_failed": self.commands_failed,
                "events_failed": self.events_failed,
                "storage_checked_at": isoformat(self.storage_checked_at),
            }

        route_base = public_base_url or (
            f"http://127.0.0.1:{self.health_server_port}" if self.health_server_port else None
        )
        routes = {
            "ping": f"{route_base}/ping" if route_base else None,
            "health": f"{route_base}/health" if route_base else None,
            "ready": f"{route_base}/health/ready" if route_base else None,
            "status_page": f"{route_base}/status" if route_base else None,
            "status_json": f"{route_base}/status.json" if route_base else None,
        }

        return {
            "service": self.service_name,
            "status": status,
            "ready": ready,
            "started_at": isoformat(self.started_at),
            "uptime_seconds": uptime_seconds,
            "uptime_human": human_duration(uptime_seconds),
            "latency_ms": latency_ms,
            "guild_count": guild_count,
            "cached_user_count": cached_users,
            "allowed_guild_id": allowed_guild_id,
            "memory_rss_mb": get_process_memory_mb(),
            "gc_counts": list(gc.get_count()),
            "checks": checks,
            "queues": {
                "commands": command_gate.snapshot(),
                "api": api_gate.snapshot(),
            },
            "runtime": summary,
            "database": storage_health,
            "issues": recent_issues,
            "routes": routes,
            "python_version": sys.version.split()[0],
            "discord_py_version": discord.__version__,
            "generated_at": isoformat(now),
        }


def build_status_html(snapshot: dict[str, Any]) -> str:
    color_map = {"ok": "#16a34a", "degraded": "#f59e0b", "error": "#ef4444"}
    badge_color = color_map.get(snapshot["status"], "#38bdf8")
    issues = snapshot.get("issues", [])

    issue_html = ""
    if issues:
        rows: list[str] = []
        for issue in issues:
            details = issue.get("details") or "-"
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(issue.get('timestamp', '-')))}</td>"
                f"<td>{html.escape(str(issue.get('severity', '-')))}</td>"
                f"<td>{html.escape(str(issue.get('source', '-')))}</td>"
                f"<td>{html.escape(str(issue.get('summary', '-')))}</td>"
                f"<td>{html.escape(str(details))}</td>"
                f"<td>{html.escape(str(issue.get('count', 1)))}</td>"
                "</tr>"
            )
        issue_html = "".join(rows)
    else:
        issue_html = (
            "<tr><td colspan='6'>Keine aktuellen Fehler oder Warnungen gespeichert.</td></tr>"
        )

    checks_html = "".join(
        (
            "<li><strong>{name}</strong>: {value}</li>".format(
                name=html.escape(key.replace("_", " ").title()),
                value="OK" if value else "Nein",
            )
        )
        for key, value in snapshot.get("checks", {}).items()
    )

    queues = snapshot.get("queues", {})
    command_queue = queues.get("commands", {})
    api_queue = queues.get("api", {})
    runtime = snapshot.get("runtime", {})
    database = snapshot.get("database", {})

    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(str(snapshot.get("service", "Bot Status")))}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #07111f;
      --panel: rgba(7, 18, 34, 0.86);
      --muted: #a7bed3;
      --line: rgba(148, 163, 184, 0.18);
      --accent: {badge_color};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(34, 211, 238, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.12), transparent 24%),
        linear-gradient(135deg, #020617 0%, #0f172a 55%, #111827 100%);
      color: #e5eef7;
    }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 28px 18px 42px; }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 26px 60px rgba(0, 0, 0, 0.28);
      backdrop-filter: blur(10px);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      border-radius: 999px;
      background: var(--accent);
      color: #fff;
      font-size: 0.84rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 16px 0 8px; font-size: 2.2rem; }}
    p {{ color: var(--muted); line-height: 1.55; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-top: 20px;
    }}
    .card {{
      background: rgba(15, 23, 42, 0.82);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
    }}
    .label {{ color: var(--muted); font-size: 0.84rem; text-transform: uppercase; letter-spacing: 0.06em; }}
    .value {{ margin-top: 8px; font-size: 1.25rem; font-weight: 700; }}
    section {{
      margin-top: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 22px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.24);
      backdrop-filter: blur(10px);
    }}
    h2 {{ margin: 0 0 14px; font-size: 1.2rem; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); }}
    li {{ margin: 6px 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.94rem; }}
    th, td {{ padding: 10px 12px; border-top: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ color: #d7e7f5; }}
    td {{ color: var(--muted); }}
    code {{ color: #67e8f9; }}
    .mono {{ font-family: Consolas, "SFMono-Regular", monospace; }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <span class="badge">{html.escape(str(snapshot.get("status", "unknown")))}</span>
      <h1>{html.escape(str(snapshot.get("service", "Bot Status")))}</h1>
      <p>Diese Website bleibt auf Render online und zeigt den Live-Zustand des Bots, letzte Fehler, Latenz, RAM und Queue-Auslastung.</p>
      <div class="grid">
        <div class="card"><div class="label">Ready</div><div class="value">{html.escape(str(snapshot.get("ready")))}</div></div>
        <div class="card"><div class="label">Guilds</div><div class="value">{html.escape(str(snapshot.get("guild_count")))}</div></div>
        <div class="card"><div class="label">Latency</div><div class="value">{html.escape(str(snapshot.get("latency_ms") or "-"))} ms</div></div>
        <div class="card"><div class="label">RAM</div><div class="value">{html.escape(str(snapshot.get("memory_rss_mb") or "-"))} MB</div></div>
        <div class="card"><div class="label">Uptime</div><div class="value">{html.escape(str(snapshot.get("uptime_human")))}</div></div>
        <div class="card"><div class="label">Login State</div><div class="value">{html.escape(str(runtime.get("login_state", "-")))}</div></div>
        <div class="card"><div class="label">Command Queue</div><div class="value">{html.escape(str(command_queue.get("running", 0)))}/{html.escape(str(command_queue.get("limit", 0)))}</div></div>
        <div class="card"><div class="label">API Queue</div><div class="value">{html.escape(str(api_queue.get("running", 0)))}/{html.escape(str(api_queue.get("limit", 0)))}</div></div>
      </div>
    </section>

    <section>
      <h2>Checks</h2>
      <ul>{checks_html}</ul>
    </section>

    <section>
      <h2>Laufzeit</h2>
      <div class="grid">
        <div class="card"><div class="label">Letztes Ready</div><div class="value mono">{html.escape(str(runtime.get("last_ready_at") or "-"))}</div></div>
        <div class="card"><div class="label">Letzter Connect-Versuch</div><div class="value mono">{html.escape(str(runtime.get("last_connect_attempt_at") or "-"))}</div></div>
        <div class="card"><div class="label">Letzter Connect-Fehler</div><div class="value">{html.escape(str(runtime.get("last_connect_error") or "-"))}</div></div>
        <div class="card"><div class="label">Storage</div><div class="value">{html.escape('OK' if database.get('ok') else 'Fehler')}</div></div>
      </div>
      <p class="mono">Routen: <code>/ping</code> <code>/health</code> <code>/health/ready</code> <code>/status</code> <code>/status.json</code></p>
    </section>

    <section>
      <h2>Letzte Fehler</h2>
      <table>
        <thead>
          <tr>
            <th>Zeit</th>
            <th>Level</th>
            <th>Quelle</th>
            <th>Zusammenfassung</th>
            <th>Details</th>
            <th>Anzahl</th>
          </tr>
        </thead>
        <tbody>{issue_html}</tbody>
      </table>
    </section>
  </main>
</body>
</html>"""


def send_json(handler: BaseHTTPRequestHandler, status_code: int, payload: dict[str, Any]) -> None:
    body = json.dumps(_json_safe(payload), ensure_ascii=True, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_text(handler: BaseHTTPRequestHandler, status_code: int, payload: str) -> None:
    body = payload.encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_html(handler: BaseHTTPRequestHandler, status_code: int, payload: str) -> None:
    body = payload.encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class StatusRequestHandler(BaseHTTPRequestHandler):
    snapshot_factory: Callable[[], dict[str, Any]] | None = None

    def do_GET(self) -> None:
        if self.snapshot_factory is None:
            send_json(
                self,
                503,
                {
                    "status": "error",
                    "message": "Snapshot noch nicht verfuegbar.",
                },
            )
            return

        path = urlsplit(self.path).path.rstrip("/") or "/"
        snapshot = self.snapshot_factory()

        if path == "/ping":
            send_text(self, 200, "pong")
            return

        if path in {"/health/live", "/health"}:
            send_json(
                self,
                200,
                {
                    "status": snapshot.get("status"),
                    "ready": snapshot.get("ready"),
                    "uptime_seconds": snapshot.get("uptime_seconds"),
                    "latency_ms": snapshot.get("latency_ms"),
                },
            )
            return

        if path == "/health/ready":
            send_json(self, 200 if snapshot.get("ready") else 503, snapshot)
            return

        if path in {"/status.json", "/health/details"}:
            send_json(self, 200, snapshot)
            return

        if path in {"/", "/status", "/health/ui"}:
            send_html(self, 200, build_status_html(snapshot))
            return

        send_json(
            self,
            404,
            {
                "status": "not_found",
                "message": "Verfuegbare Routen: /ping, /health, /health/ready, /status, /status.json",
            },
        )

    def log_message(self, format: str, *args: Any) -> None:
        return


def start_status_server(
    *,
    port: int,
    snapshot_factory: Callable[[], dict[str, Any]],
) -> ThreadingHTTPServer:
    StatusRequestHandler.snapshot_factory = snapshot_factory
    server = ThreadingHTTPServer(("0.0.0.0", port), StatusRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="status-http")
    thread.start()
    return server
