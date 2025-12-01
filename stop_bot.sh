#!/bin/bash

echo "=== Stopping Telegram Bot ==="

# Stop bot using saved PID
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    if kill -0 $BOT_PID 2>/dev/null; then
        kill $BOT_PID
        echo "Bot with PID $BOT_PID stopped"
        rm bot.pid
    else
        echo "Bot with PID $BOT_PID not running"
        rm bot.pid
    fi
else
    # Fallback: kill by process name
    if pgrep -f "telegram_bot.py" > /dev/null; then
        pkill -f "telegram_bot.py"
        echo "Bot stopped (found by process name)"
    else
        echo "No bot process found"
    fi
fi

echo "=== Bot stopped ==="