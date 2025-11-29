import subprocess
import time
import os
import requests
import sys

# Se till att log-mappen finns
os.makedirs("logs", exist_ok=True)

# Starta Ollama (Mistral) som bakgrundsprocess
ollama_log = open("logs/ollama.log", "w", encoding="utf-8")
ollama = subprocess.Popen(
    ["ollama", "run", "mistral"],
    stdout=ollama_log,
    stderr=ollama_log,
    creationflags=subprocess.DETACHED_PROCESS
)
print("✅ Ollama (Mistral) startad i bakgrunden...")

# Vänta lite så modellen hinner starta
time.sleep(5)

# Kontrollera att Ollama svarar
try:
    test = requests.post("http://localhost:11434/api/generate",
                         json={"model": "mistral", "prompt": "ping", "stream": False},
                         timeout=5)
    if test.status_code != 200:
        print("❌ Ollama svarar inte, stoppar botten.")
        sys.exit(1)
except Exception as e:
    print(f"❌ Kunde inte nå Ollama: {e}")
    sys.exit(1)

# Starta Discord-botten
bot_log = open("logs/bot.log", "w", encoding="utf-8")
bot = subprocess.Popen(
    ["python", "main.py"],
    stdout=bot_log,
    stderr=bot_log,
    creationflags=subprocess.DETACHED_PROCESS
)
print("✅ Discord-botten startad i bakgrunden...")
print("📜 Loggar skrivs till logs/ollama.log och logs/bot.log")
