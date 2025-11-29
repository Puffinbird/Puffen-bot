@echo off
echo Startar Ollama (Mistral)...
start "" /min ollama run mistral

echo Väntar lite så Ollama hinner starta...
timeout /t 5 >nul

echo Startar Discord-botten...
start "" python main.py

echo Allt är igång! Loggar finns i logs\ollama.log och logs\bot.log
pause
