#!/bin/bash

# ✅ Kontrollera att venv finns
if [ ! -f "./venv/bin/activate" ]; then
    echo "❌ venv saknas – kör 'python3 -m venv venv' först"
    exit 1
fi

# ✅ Aktivera venv
source ./venv/bin/activate

restart_bot() {
    BOT_NAME=$1
    BOT_DIR="./$BOT_NAME"
    MAIN="$BOT_DIR/main.py"
    LOG="$BOT_DIR/logs/bot.log"
    PIDFILE="$BOT_DIR/bot.pid"

    # ✅ Välj rätt TOKEN beroende på bot
    if [ "$BOT_NAME" == "Puffen" ]; then
        TOKEN_VAR="PUFFEN_TOKEN"
    elif [ "$BOT_NAME" == "Puffen-RPG" ]; then
        TOKEN_VAR="PUFFEN_RPG_TOKEN"
    else
        echo "❌ Okänd bot: $BOT_NAME"
        return
    fi

    TOKEN_VALUE=$(printenv $TOKEN_VAR)
    if [ -z "$TOKEN_VALUE" ]; then
        echo "❌ Miljövariabel '$TOKEN_VAR' saknas – kör 'export $TOKEN_VAR=...'"
        return
    fi

    # ✅ Kontrollera att main.py finns
    if [ ! -f "$MAIN" ]; then
        echo "❌ Hittar inte $MAIN – kontrollera botnamnet"
        return
    fi

    # 🛑 Stoppa gammal process om den finns
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

    # 📝 Logga omstart
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Restarted $BOT_NAME (PID: $(cat $PIDFILE))" >> ./deploy.log
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
