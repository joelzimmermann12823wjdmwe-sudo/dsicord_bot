$Host.UI.RawUI.WindowTitle = "Neon Bot Launcher"
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   NEON BOT — LAUNCHER" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Token-Check
$env = Get-Content "NeonBot\.env" -Raw -ErrorAction SilentlyContinue
if ($env -match "DISCORD_TOKEN=DEIN_TOKEN_HIER") {
    Write-Host "[!] Kein Token eingetragen!" -ForegroundColor Red
    Write-Host "    Oeffne NeonBot\.env und trage deinen Token ein." -ForegroundColor Yellow
    Write-Host ""
    Start-Process notepad "NeonBot\.env"
    pause; exit
}

Write-Host "  Starte Neon Bot..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
    "-NoExit","-Command",
    "`$Host.UI.RawUI.WindowTitle='Neon Bot';" +
    "`$Host.UI.RawUI.BackgroundColor='DarkBlue';" +
    "Clear-Host;" +
    "Write-Host '======================================' -ForegroundColor Cyan;" +
    "Write-Host '   NEON BOT laeuft!' -ForegroundColor Cyan;" +
    "Write-Host '======================================' -ForegroundColor Cyan;" +
    "Write-Host '';" +
    "cd NeonBot\bot;" +
    "python main.py;" +
    "Write-Host '';" +
    "Write-Host 'Bot gestoppt!' -ForegroundColor Red;" +
    "pause"
)

Write-Host "[OK] Bot gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "  Blaues Fenster offen lassen = Bot laeuft!" -ForegroundColor White
Write-Host ""
pause
