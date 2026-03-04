import threading
import os
import subprocess

def run_dashboard():
    print("🌐 Starte Dashboard...")
    subprocess.run(["python", "dashboard/app.py"])

def run_bot():
    print("🤖 Starte Discord Bot...")
    subprocess.run(["python", "bot/main.py"])

if __name__ == "__main__":
    # Dashboard in einem eigenen Thread starten
    threading.Thread(target=run_dashboard).start()
    # Bot im Haupt-Thread starten
    run_bot()