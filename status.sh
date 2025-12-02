#!/bin/bash

check_bot() {
    BOT_NAME=$1
    PIDFILE="./$BOT_NAME/bot.pid"

    if [ ! -f "$PIDFILE" ]; then
        echo "🔍 $BOT_NAME: Ingen pid-fil – botten körs troligen inte"
        return
    fi

    PID=$(cat "$PIDFILE")
    if ps -p $PID > /dev/null; then
        echo "✅ $BOT_NAME körs (PID: $PID)"
    else
        echo "⚠️ $BOT_NAME har pid-fil men processen är död (PID: $PID)"
    fi
}

echo "📊 Botstatus:"
check_bot "Puffen"
check_bot "Puffen-RPG"
