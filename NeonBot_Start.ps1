# ============================================================
#   NEON BOT - Start Script
# ============================================================

$Host.UI.RawUI.WindowTitle = "Neon Bot - Launcher"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "        ⚡  NEON BOT  LAUNCHER  ⚡         " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Pruefen ob NeonBot Ordner existiert
if (-not (Test-Path "NeonBot")) {
    Write-Host "[FEHLER] Kein 'NeonBot' Ordner gefunden!" -ForegroundColor Red
    Write-Host "Stelle sicher, dass du das Script im richtigen Ordner ausfuehrst." -ForegroundColor Yellow
    pause; exit
}

# Python pruefen
try {
    $v = python --version 2>&1
    Write-Host "[OK] $v" -ForegroundColor Green
} catch {
    Write-Host "[FEHLER] Python nicht gefunden!" -ForegroundColor Red
    pause; exit
}

# Token pruefen
$env = Get-Content "NeonBot\.env" -Raw
if ($env -match "DISCORD_TOKEN=DEIN_BOT_TOKEN_HIER") {
    Write-Host "[WARNUNG] Kein Bot-Token in .env eingetragen!" -ForegroundColor Yellow
    Write-Host "Oeffne NeonBot\.env und trage deinen Token ein." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Trotzdem starten? (j/n)" -ForegroundColor Yellow
    $a = Read-Host
    if ($a -ne "j" -and $a -ne "J") { exit }
}

# GUILD_IDS pruefen
if ($env -match "GUILD_IDS=DEINE_SERVER_ID") {
    Write-Host "[WARNUNG] Keine GUILD_IDS in .env! Commands werden nicht sofort verfuegbar sein." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Starte Neon Bot..." -ForegroundColor Cyan
Write-Host ""

# Bot in eigenem Fenster starten
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& {" +
    "`$Host.UI.RawUI.WindowTitle = 'Neon Bot';" +
    "`$Host.UI.RawUI.BackgroundColor = 'DarkBlue';" +
    "Clear-Host;" +
    "Write-Host '===========================================' -ForegroundColor Cyan;" +
    "Write-Host '   NEON BOT laeuft — Fenster offen lassen!' -ForegroundColor Cyan;" +
    "Write-Host '===========================================' -ForegroundColor Cyan;" +
    "Write-Host '';" +
    "Set-Location 'NeonBot\bot';" +
    "python main.py;" +
    "Write-Host '';" +
    "Write-Host 'Bot gestoppt. Druecke eine Taste...' -ForegroundColor Red;" +
    "pause" +
    "}"
)

Write-Host "[OK] Bot gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Bot laeuft im blauen Fenster." -ForegroundColor White
Write-Host "  Fenster schliessen = Bot stoppen." -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Druecke eine Taste um den Launcher zu schliessen..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
