#!/bin/bash
# Script to start automatic email services for reservations
# Run this script to start automatic reminder and summary sending

cd "$(dirname "$0")"
source .venv/bin/activate

echo "🚀 Starting automatic email services..."
echo ""

# Start reminder service in background (checks every 5 minutes)
echo "📧 Starting reminder service (checks every 5 minutes)..."
python manage.py auto_send_reminders --interval 300 > logs/reminders.log 2>&1 &
REMINDER_PID=$!
echo $REMINDER_PID > .reminder_pid
echo "   Reminder service started (PID: $REMINDER_PID)"

# Wait a bit
sleep 2

echo ""
echo "✅ Services started!"
echo ""
echo "To stop services, run: ./stop_email_services.sh"
echo "Or manually: kill $REMINDER_PID"
echo ""
echo "Logs:"
echo "  - Reminders: logs/reminders.log"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

