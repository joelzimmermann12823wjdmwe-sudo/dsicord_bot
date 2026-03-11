import subprocess
import sys
import time

print("--- STARTE MULTI-BOT-SYSTEM ---")
p1 = subprocess.Popen([sys.executable, "bot/neon_main.py"])
p2 = subprocess.Popen([sys.executable, "status/status_main.py"])

p1.wait()
p2.wait()
