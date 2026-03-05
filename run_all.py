import subprocess
import sys

print("Starte NeonBot System...")

# Startet das Flask Dashboard im Hintergrund
flask_process = subprocess.Popen([sys.executable, "dashboard/app.py"])

# Startet den Discord Bot im Vordergrund
bot_process = subprocess.Popen([sys.executable, "main.py"])

try:
    flask_process.wait()
    bot_process.wait()
except KeyboardInterrupt:
    print("\nBeende alle Prozesse...")
    flask_process.terminate()
    bot_process.terminate()