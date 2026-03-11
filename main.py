import subprocess
import sys
import time
import os

# Dieses Skript startet beide Bots als separate Prozesse.
# Um "429 Too Many Requests" zu vermeiden, starten wir sie zeitversetzt.

def start_bots():
    print("--- STARTE NEON MULTI-BOT-SYSTEM ---")
    
    # 1. Den Hauptbot starten
    print("🚀 Starte Hauptbot...")
    main_bot = subprocess.Popen([sys.executable, "bot/neon_main.py"])
    
    # 2. WARTEN (Wichtig!)
    # Wir warten 30 Sekunden, bevor der zweite Bot anklopft, 
    # um das Rate-Limit zu umgehen.
    print("⏳ Warte 30 Sekunden vor dem Start des Statusbots...")
    time.sleep(30)
    
    # 3. Den Statusbot starten
    print("🚀 Starte Statusbot...")
    status_bot = subprocess.Popen([sys.executable, "status/status_main.py"])

    try:
        while True:
            # Überprüfen, ob einer der Prozesse beendet wurde
            if main_bot.poll() is not None:
                print("⚠️ Hauptbot gestoppt. Warte 15s und starte neu...")
                time.sleep(15)
                main_bot = subprocess.Popen([sys.executable, "bot/neon_main.py"])
            
            if status_bot.poll() is not None:
                print("⚠️ Statusbot gestoppt. Warte 15s und starte neu...")
                time.sleep(15)
                status_bot = subprocess.Popen([sys.executable, "status/status_main.py"])
            
            time.sleep(10)
    except KeyboardInterrupt:
        main_bot.terminate()
        status_bot.terminate()

if __name__ == "__main__":
    start_bots()