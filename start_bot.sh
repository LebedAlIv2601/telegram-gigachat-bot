#!/bin/bash

echo "=== Starting Telegram Bot in Background ==="

cd /Users/aleksandrlebed/PycharmProjects/AiChallenge

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Kill existing bot process if running
if pgrep -f "telegram_bot.py" > /dev/null; then
    echo "Stopping existing bot..."
    pkill -f "telegram_bot.py"
    sleep 2
fi

# Start bot in background with output logging
echo "Starting bot in background..."
nohup python telegram_bot.py > bot.log 2>&1 &

# Get process ID
BOT_PID=$!
echo "Bot started with PID: $BOT_PID"
echo "Bot PID saved to bot.pid"
echo $BOT_PID > bot.pid

echo "=== Bot Commands ==="
echo "Check status: ./check_bot.sh"
echo "Stop bot: ./stop_bot.sh"
echo "View logs: tail -f bot.log"
echo "=== Bot is now running independently! ==="