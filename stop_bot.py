import os
import signal

# Stäng Ollama
os.system("taskkill /F /IM ollama.exe")

# Stäng Discord-botten (Python-processen)
os.system("taskkill /F /IM python.exe")

print("🛑 Ollama och Discord-botten stoppades.")
