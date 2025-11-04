#!/bin/bash
# Script to stop automatic email services

cd "$(dirname "$0")"

if [ -f .reminder_pid ]; then
    REMINDER_PID=$(cat .reminder_pid)
    if ps -p $REMINDER_PID > /dev/null 2>&1; then
        kill $REMINDER_PID
        echo "✅ Reminder service stopped (PID: $REMINDER_PID)"
        rm .reminder_pid
    else
        echo "⚠️  Reminder service not running"
        rm .reminder_pid
    fi
else
    echo "⚠️  No reminder service PID file found"
fi

