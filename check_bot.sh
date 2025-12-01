#!/bin/bash

echo "=== Bot Status Check ==="

# Check if bot process is running
if pgrep -f "telegram_bot.py" > /dev/null; then
    BOT_PID=$(pgrep -f "telegram_bot.py")
    echo "✅ Bot is RUNNING (PID: $BOT_PID)"
    
    # Show memory and CPU usage
    echo "📊 Resource usage:"
    ps -p $BOT_PID -o pid,ppid,%cpu,%mem,etime,comm
    
    # Show recent log entries
    if [ -f "bot.log" ]; then
        echo ""
        echo "📋 Recent logs (last 10 lines):"
        tail -10 bot.log
    fi
else
    echo "❌ Bot is NOT running"
    
    # Check for error logs
    if [ -f "bot.log" ]; then
        echo ""
        echo "📋 Last error logs:"
        tail -20 bot.log | grep -i error
    fi
fi

echo ""
echo "=== Commands ==="
echo "Start bot: ./start_bot.sh"
echo "Stop bot: ./stop_bot.sh"
echo "View full logs: tail -f bot.log"