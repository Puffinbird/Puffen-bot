#!/bin/bash

source ./venv/bin/activate

BOT_NAME=$1

if [ -z "$BOT_NAME" ]; then
    echo "❌ Ange botnamn som parameter: ./stop.sh Puffen-RPG"
    exit 1
fi

PIDFILE="./$BOT_NAME/bot.pid"

if [ ! -f "$PIDFILE" ]; then
    echo "⚠️ Ingen pid-fil hittades för $BOT_NAME – kanske kör den inte?"
    exit 1
fi

PID=$(cat "$PIDFILE")

if ps -p $PID > /dev/null; then
    kill $PID
    echo "🛑 Stängde $BOT_NAME (PID: $PID)"
else
    echo "⚠️ Processen med PID $PID körs inte längre"
fi

rm "$PIDFILE"
