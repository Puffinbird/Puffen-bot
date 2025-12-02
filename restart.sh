#!/bin/bash

if [ ! -f "./venv/bin/activate" ]; then
    echo "❌ venv saknas eller är trasig – kör 'python3 -m venv venv' först"
    exit 1
fi

source ./venv/bin/activate


source ./venv/bin/activate

restart_bot() {
    BOT_NAME=$1
    BOT_DIR="./$BOT_NAME"
    MAIN="$BOT_DIR/main.py"
    LOG="$BOT_DIR/logs/bot.log"
    PIDFILE="$BOT_DIR/bot.pid"

    if [ ! -f "$MAIN" ]; then
        echo "❌ Hittar inte $MAIN – kontrollera botnamnet"
        return
    fi

    if [ -f "$PIDFILE" ]; then
        OLD_PID=$(cat "$PIDFILE")
        if ps -p $OLD_PID > /dev/null; then
            kill $OLD_PID
            echo "🛑 Stoppade gammal process ($BOT_NAME, PID: $OLD_PID)"
        fi
        rm "$PIDFILE"
    fi

    echo "📦 Hämtar senaste kod för $BOT_NAME..."
    git pull origin main

    echo "🚀 Startar $BOT_NAME..."
    nohup python3 "$MAIN" > "$LOG" 2>&1 &
    echo $! > "$PIDFILE"

    echo "✅ $BOT_NAME är nu omstartad (PID: $(cat $PIDFILE))"
}

BOT_NAME=$1

if [ -z "$BOT_NAME" ]; then
    echo "❌ Ange botnamn som parameter: ./restart.sh Puffen-RPG eller ./restart.sh all"
    exit 1
fi

if [ "$BOT_NAME" == "all" ]; then
    restart_bot "Puffen"
    restart_bot "Puffen-RPG"
else
    restart_bot "$BOT_NAME"
fi

# Logga omstart
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Restarted $BOT_NAME (PID: $(cat $PIDFILE))" >> ./deploy.log
