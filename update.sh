#!/bin/bash

BOT_NAME=$1

if [ -z "$BOT_NAME" ]; then
    echo "❌ Ange botnamn som parameter: ./update.sh Puffen-RPG"
    exit 1
fi

BOT_DIR="./$BOT_NAME"
MAIN="$BOT_DIR/main.py"
LOG="$BOT_DIR/logs/bot.log"
PIDFILE="$BOT_DIR/bot.pid"

if [ ! -f "$MAIN" ]; then
    echo "❌ Hittar inte $MAIN – kontrollera botnamnet"
    exit 1
fi

if [ -z "$TOKEN" ]; then
    echo "❌ TOKEN saknas i miljön! Sätt den med 'export TOKEN=...'"
    exit 1
fi

echo "📦 Uppdaterar repo..."
git pull origin main

echo "🧹 Stoppar eventuell gammal process..."
if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    if ps -p $OLD_PID > /dev/null; then
        kill $OLD_PID
        echo "🛑 Stoppade gammal process ($OLD_PID)"
    fi
    rm "$PIDFILE"
fi

echo "🚀 Startar $BOT_NAME..."
nohup python3 "$MAIN" > "$LOG" 2>&1 &
echo $! > "$PIDFILE"

echo "✅ $BOT_NAME körs i bakgrunden (PID: $(cat $PIDFILE))"
